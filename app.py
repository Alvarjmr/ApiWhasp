from flask import Flask,request,Response,jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    mensajes_log.append(texto)
    #guardamos el mensaje en la base de datos
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
    data = req.get_json()
    agregar_mensajes_log(data)
    return jsonify({'status': 'EVENT_RECEIVED'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
