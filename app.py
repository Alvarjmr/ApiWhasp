from flask import Flask, json,render_template
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

    prueba1= log(texto="Primer registro de prueba")
    prueba2= log(texto="Segundo registro de prueba")
    db.session.add(prueba1)
    db.session.add(prueba2)
    db.session.commit()

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

#agregar_mensajes_log(json.dumps("Aplicacion iniciada"))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
