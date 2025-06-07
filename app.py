from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinica.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)    

class Paciente(db.Model):
    __tablename__ = 'paciente'
    dni = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tel = db.Column(db.String(10))
    def __repr__(self):
        return f"<Paciente: {self.nombre} - DNI: {self.dni}>"

class Turno(db.Model):
    __tablename__ = 'turno'
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.Integer, db.ForeignKey('paciente.dni'), nullable=False)
    matricula = db.Column(db.BigInteger, nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    matricula = db.Column(db.Integer, db.ForeignKey('medico.matricula'), nullable=False)

class Medico(db.Model):
    __tablename__ = 'medico'
    matricula = db.Column(db.Integer, primary_key=True, nullable=False) 
    nombre = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    tel = db.Column(db.String(20), nullable=False)
    def __repr__(self):
        return f"<Medico: {self.nombre} - Matricula: {self.matricula}>"

class HistoriaClinica(db.Model):
    __tablename__ = 'historia'
    id = db.Column(db.Integer, primary_key=True)
    dni_paciente = db.Column(db.Integer, db.ForeignKey('paciente.dni'), nullable=False)
    matricula_medico = db.Column(db.Integer, db.ForeignKey('medico.matricula'), nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/cargar_paciente', methods=['GET', 'POST'])
def cargar_paciente():
    if request.method == 'POST':
        dni = int(re.sub(r"\D", "", request.form['dni']))
        nombre = request.form['nombre']
        tel = request.form['tel']

        # Verificamos si ya existe ese DNI
        if Paciente.query.get(dni):
            return render_template('cargar_paciente.html', error="El paciente ya existe.")

        paciente = Paciente(dni=dni, nombre=nombre, tel=tel)
        db.session.add(paciente)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('cargar_paciente.html')


@app.route('/cargar_turno', methods=['GET', 'POST'])
def cargar_turno():
    especialidades = db.session.query(Medico.especialidad).distinct().all()
    especialidades = [e[0] for e in especialidades]

    if request.method == 'POST':
        fecha = request.form['fecha']
        dni = int(re.sub(r"\D", "", request.form['dni']))
        especialidad = request.form['especialidad']
        estado = request.form['estado']
        paciente = Paciente.query.get(dni)

        if not paciente:
            return render_template('cargar_turno.html', especialidades=especialidades, error="Paciente no registrado.")

        medico = Medico.query.filter_by(especialidad=especialidad).first()
        if not medico:
            return render_template('cargar_turno.html', especialidades=especialidades, error="No hay médico con esa especialidad.")

        turno = Turno(fecha=fecha, dni=dni, matricula=medico.matricula, estado=estado)
        db.session.add(turno)

        # ✅ Crear historia clínica antes del commit
        nueva_historia = HistoriaClinica(
            dni_paciente=dni,
            matricula_medico=medico.matricula,
            fecha=fecha,
            descripcion="Pendiente de completar"
        )
        db.session.add(nueva_historia)

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('cargar_turno.html', especialidades=especialidades)


def get_especialidades():
    especialidades = db.session.query(Medico.especialidad).distinct().all()
    return [e[0] for e in especialidades]


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

@app.route('/delete/<int:dni>', methods=['POST'])
def delete(dni):
    paciente = Paciente.query.get_or_404(dni)
    db.session.delete(paciente)
    db.session.commit()
    return redirect(url_for('ver_pacientes'))

@app.route('/ver_turnos')
def ver_turnos():
    turnos = Turno.query.all()
    datos = []
    for turno in turnos:
        medico = Medico.query.get(turno.matricula)
        datos.append({
            'turno': turno,
            'especialidad': medico.especialidad if medico else 'No asignada'
        })
    return render_template('vistat.html', datos=datos)


@app.route('/editar_turno/<int:id>', methods=['GET', 'POST'])
def editar_turno(id):
    turno = Turno.query.get_or_404(id)
    especialidades = get_especialidades()

    historia = HistoriaClinica.query.filter_by(
    dni_paciente=turno.dni,
    matricula_medico=turno.matricula,
    fecha=turno.fecha
    ).first()

     
    if request.method == 'POST':
        fecha = request.form['fecha']
        estado = request.form['estado']

        # Guardamos datos clave antes de borrar
        dni = turno.dni
        matricula = turno.matricula

        # Eliminamos el turno anterior
        db.session.delete(turno)
        db.session.commit()

        # Creamos el nuevo turno actualizado
        nuevo_turno = Turno(
            dni=dni,
            matricula=matricula,
            fecha=fecha,
            estado=estado
        )
        db.session.add(nuevo_turno)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('editar_turno.html', turno=turno, especialidades=especialidades, historia=historia)

if __name__ == '__main__':
    app.run(debug=True)
