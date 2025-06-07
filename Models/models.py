from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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