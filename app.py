from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinica.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Paciente(db.Model):
    __tablename__ = 'paciente'
    dni = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tel = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Paciente: {self.nombre} - DNI: {self.dni}>"

class Turno(db.Model):
    __tablename__ = 'turno'
    id = db.Column(db.Integer, primary_key=True)
    dni_paciente = db.Column(db.BigInteger, db.ForeignKey('paciente.dni'), nullable=False)
    matricula = db.Column(db.BigInteger, nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    hora = db.Column(db.String(10), nullable=False)
    estado = db.Column(db.String(20), nullable=False)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/cargar_paciente', methods=['GET', 'POST'])
def cargar_paciente():
    if request.method == 'POST':
        dni = int(request.form['dni'])
        nombre = request.form['nombre']
        tel = request.form['tel']
        paciente = Paciente(dni=dni, nombre=nombre, tel=tel)
        db.session.add(paciente)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('cargar_paciente.html')


@app.route('/cargar_turno', methods=['GET', 'POST'])
def cargar_turno():
    if request.method == 'POST':
        dni = int(request.form['dni'])
        matricula = int(request.form['matricula'])
        fecha = request.form['fecha']
        hora = request.form['hora']
        estado = request.form['estado']
        turno = Turno(dni_paciente=dni, matricula=matricula, fecha=fecha, hora=hora, estado=estado)
        db.session.add(turno)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('/ cargar_turno.html')


@app.route('/vistap')
def ver_pacientes():
    pacientes = Paciente.query.all()
    return render_template('vistap.html', pacientes=pacientes)


@app.route('/edit/<int:dni>', methods=['GET', 'POST'])
def edit(dni):
    paciente = Paciente.query.get_or_404(dni)
    if request.method == 'POST':
        paciente.nombre = request.form['nombre']
        paciente.tel = request.form['tel']
        db.session.commit()
        return redirect(url_for('ver_pacientes'))
    return render_template('edit.html', paciente=paciente)

@app.route('/delete/<int:dni>')
def delete(dni):
    paciente = Paciente.query.get_or_404(dni)
    db.session.delete(paciente)
    db.session.commit()
    return redirect(url_for('ver_pacientes'))

if __name__ == '__main__':
    app.run(debug=True)
