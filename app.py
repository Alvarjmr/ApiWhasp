from flask import Flask,request,Response,jsonify,json,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client

app = Flask(__name__)
#configuracion de la bse de datos
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False 
db= SQLAlchemy(app)

#definicion del modelo
class log(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto= db.Column(db.TEXT)
#creacion de la base de datos
with app.app_context():
    db.create_all()
   

#funcion para ordenar los registros por fecha y hora
def ordenar_logs_por_fecha(logs):   
    return sorted(logs, key=lambda x: x.fecha_hora, reverse=True)

@app.route('/')
def index():
    #obtenemos todos los registros de la tabla log
    logs= log.query.all()
    logs_ordenados= ordenar_logs_por_fecha(logs)
    return render_template('index.html', logs=logs_ordenados)

mensajes_log = []
#funcion para agregar mensajes al log
def agregar_mensajes_log(texto):
    # si llega un dict (webhook), lo convertimos a JSON
    if isinstance(texto, (dict, list)):
        texto = json.dumps(texto, ensure_ascii=False, indent=2)

    mensajes_log.append(texto)

    nuevo_registro = log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

#token de autenticacion
TOKEN_ANDERCODE = 'ANDERCODE'
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return verificar_token(request)
    elif request.method == 'POST':
        return recibir_mensaje(request)

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if token == TOKEN_ANDERCODE:
        return Response(challenge, status=200, mimetype='text/plain')
    else:
        return Response('Token inválido', status=403)

def recibir_mensaje(req):
    #data = req.get_json()
    #agregar_mensajes_log(data)

    try:
        data = req.get_json()
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensajes = value['messages']

        if objeto_mensajes:
            messages = objeto_mensajes[0]

            if "type" in messages:
                tipo_mensaje = messages['type']

                if tipo_mensaje == 'interactive':
                    return 0
                if "text" in messages:
                    texto_mensaje = messages['text']['body']
                    numero_telefono = messages['from']
                    enviar_respuesta_whatsapp(texto_mensaje,numero_telefono)            
                    
             # Aquí puedes procesar el mensaje recibido según tus necesidades        
        return jsonify({'messages': 'EVENT_RECEIVED'}), 200
    except Exception as e:
        return jsonify({'messages': 'EVENT_RECEIVED'}), 200


def enviar_respuesta_whatsapp(texto,number):
        texto = texto.lower()

        if "hola" in texto:
            data={
                  "messaging_product": "whatsapp",    
                  "recipient_type": "individual",
                  "to": number,
                  "type": "text",
                  "text": {
                      "preview_url": False,
                      "body": "Hola, ¿Como estas? Bienvenido?"}
                      }
        else:
            data={
                  "messaging_product": "whatsapp",    
                  "recipient_type": "individual",
                  "to": number,
                  "type": "text",
                  "text": {
                      "preview_url": False,
                      "body": "Hola visita nuestro sitio web https://andercode.net\n¿En qué puedo ayudarte?\n1. Soporte Técnico\n2. Ventas\n3. Otros"}
                      }
        # Convertir el diccionario a una cadena JSON
        data = json.dumps(data)

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer EAAT3fcXOGLoBQo6KOO1ELp6wpf30ElDLV2xX8owNT8StvSkTWxb7mZAZAACYuQjiCri9v9XBZC22ot74nq8FJtgUc5ON4YInbWTBB7tHkN4w0g5ErFqXrqULXt4ZB7GDJDSJ95hoNp4VMlpcpjbbvQjqDHcfUCLUar6KhCbTsTDDZC45su6qd1wTl5mP29gLuluq9LLsePsN1HGjL169KxBtvdA10MeVJpdzRmG7Yhw3z2BjVlkOQsNBwtzv7AKBPbfLv6FsZAoZCLSqyZCzuZC0KGX4YrqnEVhPg"
            }
        
        conn = http.client.HTTPSConnection("graph.facebook.com")

        try:
            conn.request("POST", "/v22.0/357096730823962/messages", data, headers)
            response = conn.getresponse()
            print(response.status, response.reason)
            
            
            
        except Exception as e:
            agregar_mensajes_log(json.dumps(e))
        finally:
            conn.close()
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
