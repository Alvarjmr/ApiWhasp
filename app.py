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
    
    try:
        data = req.get_json()
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensajes = value['messages']

        if objeto_mensajes:
            messages = objeto_mensajes[0]

            if "type" in messages:
                # guadar log en DB 
                tipo_mensaje = messages['type']
                agregar_mensajes_log(json.dumps(tipo_mensaje))

                if tipo_mensaje == 'interactive':
                    return 0
                if "text" in messages:
                    texto_mensaje = messages['text']['body']
                    numero_telefono = messages['from']
                    enviar_respuesta_whatsapp(texto_mensaje,numero_telefono)
                    # guadar log en DB 
                    agregar_mensajes_log(json.dumps(messages))
                                                 
                    
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
        elif "1" in texto:
            data={
                  "messaging_product": "whatsapp",    
                  "recipient_type": "individual",
                  "to": number,
                  "type": "text",
                  "text": {
                      "preview_url": False,
                      "body": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."}
                      }
        elif "2" in texto:
            data={
                  "messaging_product": "whatsapp",
                  "recipient_type": "individual",
                  "to": number,
                  "type": "location",
                  "location": {
                  "latitude": "6.265970723356335",
                  "longitude": "-75.55436370445392",
                  "name": "domino",
                  "address": "medellin"
                }
                }
        elif "3" in texto:
            data={
                  "messaging_product": "whatsapp",    
                  "recipient_type": "individual",
                  "to": number,
                  "type": "document",
                  "document": {
                      "link": "https://www.renfe.com/content/dam/renfe/es/General/PDF-y-otros/Ejemplo-de-descarga-pdf.pdf",
                      "caption": "Aquí está el documento que solicitaste."
                  }
                }
        elif "4" in texto:
            data={
                 "messaging_product": "whatsapp",
                 "to": number,
                "text": {
                "preview_url": True,
                "body": "Please visit https://www.youtube.com/watch?v=RB-RcX5DS5A&list=RDRB-RcX5DS5A&start_radio=1"      
                 }
               }
        elif "boton" in texto:
            data={
                 "messaging_product": "whatsapp",
                 "to": number,
                 "text": "interactive", 
                 "interactive": {
                     "type": "button",
                     "body": {
                         "text": "¿Confirmar tu registro?"
                     },
                     "footer": {
                         "text": "Seleccione una opciónes"
                 },
                     "action": {
                            "buttons": [
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "btnsi",
                                        "title": "Si"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "btnno",
                                        "title": "No"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "bttalvez",
                                        "title": "Tal vez"
                                    }
                                }
                            ]
                         
                     }
                 }
        }
        else:
            data={
                  "messaging_product": "whatsapp",    
                  "recipient_type": "individual",
                  "to": number,
                  "type": "text",
                  "text": {
                      "preview_url": False,
                      "body": "Hola visita nuestro sitio web https://andercode.net\n¿En qué puedo ayudarte?\n1. Soporte Técnico\n2. Ventas\n3. Otros\n4. Ver un video"}
                      }
        # Convertir el diccionario a una cadena JSON
        data = json.dumps(data)

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer EAAT3fcXOGLoBQsMh4hRth96rjNS66KH44NrILvqWOZAo0tfZBZCSOZBZACZCz7NzguWAkNPF4NNsYoS9ZAZAcSQZB6GPmVhiNUr3UNFentgXM3Sm8qZA1o2ZB5wECr4zyt9XsnMreLjKJjaV590cBjXxi7A0xacNi4i9zfGC8lUZBhEiepN75ekaOxw2K33TRBa4ikS0gqHVSfx91OVSu6rCoyZB9ubxUppeGoKhK2kMvTWJ7zwq5IU1To9IuyvVzByoLjyT8YtUpl2qiBxzYZCuvZCyZASnKrwN0CIHl3Tv"
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
