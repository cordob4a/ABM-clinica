from flask import Flask, render_template, request, redirect, url_for,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import re

app = Flask(__name__)
app.secret_key = 'admin'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinica.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)   

class Usuario(db.Model):
    __tablename__ = 'usuario'
    usuario = db.Column(db.String(100))
    pw = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), nullable=False)
    id = db.Column(db.Integer,nullable=False, primary_key=True)  # 'admin',  'paciente'

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
    fecha = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False)
    matricula = db.Column(db.Integer, db.ForeignKey('medico.matricula'), nullable=False)

class Medico(db.Model):
    __tablename__ = 'medico'
    matricula = db.Column(db.Integer, primary_key=True, nullable=False) 
    nombre = db.Column(db.String(100), nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)
    tel = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), default='activo')
    def __repr__(self):
        return f"<Medico: {self.nombre} - Matricula: {self.matricula}>"

class HistoriaClinica(db.Model):
    __tablename__ = 'historia'
    id = db.Column(db.Integer, primary_key=True)
    dni_paciente = db.Column(db.Integer, db.ForeignKey('paciente.dni'), nullable=False)
    matricula_medico = db.Column(db.Integer, db.ForeignKey('medico.matricula'), nullable=False)
    fecha = db.Column(db.String(20), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        pw = request.form['pw']
        user = Usuario.query.filter_by(usuario=usuario, pw=pw).first()
        if user:
            session['usuario'] = user.usuario
            session['rol'] = user.rol
            return redirect(url_for('index'))
            
        else:
            return render_template('login.html', error='Usuario o contraseña incorrectos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/historial/<int:dni>', methods=['GET', 'POST'])
def ver_historial(dni):
    especialidad_filtro = request.form.get('especialidad') if request.method == 'POST' else None

    # Obtener todas las especialidades de las historias del paciente
    especialidades = db.session.query(Medico.especialidad).join(HistoriaClinica, Medico.matricula == HistoriaClinica.matricula_medico)\
        .filter(HistoriaClinica.dni_paciente == dni).distinct().all()
    especialidades = [e[0] for e in especialidades]

    # Obtener el historial clínico del paciente con o sin filtro
    query = db.session.query(HistoriaClinica.fecha, HistoriaClinica.descripcion,
                             Medico.especialidad)\
             .join(Medico, HistoriaClinica.matricula_medico == Medico.matricula)\
             .filter(HistoriaClinica.dni_paciente == dni)

    if especialidad_filtro:
        query = query.filter(Medico.especialidad == especialidad_filtro)

    historial = query.order_by(HistoriaClinica.fecha.desc()).all()

    datos = [{
        'dni': dni,
        'fecha': h.fecha,
        'especialidad': h.especialidad,
        'descripcion': h.descripcion
    } for h in historial]

    return render_template('historial_clinico.html',
                           historial=datos,
                           especialidades=especialidades,
                           seleccionada=especialidad_filtro)

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

        # Crear usuario tipo paciente
        dni_str = str(dni)
        usuario = Usuario(
            usuario=dni_str,
            pw=nombre.lower() + dni_str[-4:],
            rol='paciente')
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('index'))




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

        # 🔧 Buscar médicos activos con esa especialidad
        medicos = Medico.query.filter_by(especialidad=especialidad, estado='activo').all()

        medico_disponible = None
        for m in medicos:
            cantidad_turnos = Turno.query.filter_by(matricula=m.matricula, fecha=fecha).count()
            if cantidad_turnos < 10:
                medico_disponible = m
                break  # ✅ salir cuando se encuentra uno válido

        if not medico_disponible:
            return render_template('cargar_turno.html', especialidades=especialidades,
                                   error="No hay médico disponible para esa especialidad en esa fecha.")

        # Validar que el paciente no tenga un turno en esa fecha
        turno_existente = Turno.query.filter_by(dni=dni, fecha=fecha).first()
        if turno_existente:
            return render_template('cargar_turno.html', especialidades=especialidades,
                                   error="El paciente ya tiene un turno para esa fecha.")

        # ✅ Crear turno
        turno = Turno(fecha=fecha, dni=dni, matricula=medico_disponible.matricula, estado=estado)
        db.session.add(turno)

        # ✅ Crear historia clínica
        nueva_historia = HistoriaClinica(
            dni_paciente=dni,
            matricula_medico=medico_disponible.matricula,
            fecha=fecha,
            descripcion="Pendiente de completar"
        )
        db.session.add(nueva_historia)

        db.session.commit()
        return redirect(url_for('index'))

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

@app.route('/ver_turnos', methods=['GET', 'POST'])
def ver_turnos():
    especialidades = [e[0] for e in db.session.query(Medico.especialidad).distinct().all()]
    turnos_query = Turno.query

    if request.method == 'POST':
        dni = request.form.get('dni')
        fecha = request.form.get('fecha')
        estado = request.form.get('estado')
        especialidad = request.form.get('especialidad')

        if dni:
            turnos_query = turnos_query.filter_by(dni=dni)
        if fecha:
            turnos_query = turnos_query.filter_by(fecha=fecha)
        if estado:
            turnos_query = turnos_query.filter_by(estado=estado)
        if especialidad and especialidad.strip():
            turnos_query = turnos_query.join(Medico, Turno.matricula == Medico.matricula)\
                                       .filter(func.lower(func.trim(Medico.especialidad)) == especialidad.strip().lower())

    turnos = turnos_query.all()

    datos = []
    for turno in turnos:
        medico = Medico.query.get(turno.matricula)
        datos.append({
            'turno': turno,
            'especialidad': medico.especialidad if medico else 'No asignada'
        })

    return render_template('vistat.html', datos=datos, especialidades=especialidades)

@app.route('/editar_turno/<int:id>', methods=['GET', 'POST'])
def editar_turno(id):
    turno = Turno.query.get_or_404(id)
    especialidades = get_especialidades()

    # Buscamos la historia clínica asociada al turno
    historia = HistoriaClinica.query.filter_by(
        dni_paciente=turno.dni,
        matricula_medico=turno.matricula,
        fecha=turno.fecha
    ).first()

    if request.method == 'POST':
        # ✅ Solo dentro del POST extraemos estos valores
        nueva_fecha = request.form['fecha']
        estado = request.form['estado']
        descripcion = request.form['descripcion']

        # Guardamos valores previos
        dni = turno.dni
        matricula = turno.matricula

        # Eliminamos turno viejo
        db.session.delete(turno)
        db.session.commit()

        # Creamos nuevo turno
        nuevo_turno = Turno(
            dni=dni,
            matricula=matricula,
            fecha=nueva_fecha,
            estado=estado
        )
        db.session.add(nuevo_turno)

        # Actualizamos historia clínica si existe
        if historia:
            historia.fecha = nueva_fecha
            historia.descripcion = descripcion
        else:
            nueva_historia = HistoriaClinica(
                dni_paciente=dni,
                matricula_medico=matricula,
                fecha=nueva_fecha,
                descripcion=descripcion
            )
            db.session.add(nueva_historia)

        db.session.commit()
        return redirect(url_for('index'))

    # Si GET, mostramos el formulario con los datos actuales
    return render_template('editar_turno.html', turno=turno, especialidades=especialidades, historia=historia)

if __name__ == '__main__':
    app.run(debug=True)
