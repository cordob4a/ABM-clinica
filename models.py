from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Paciente(db.Model):
    __tablename__ = 'paciente'
    dni = db.Column(db.BigInteger, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tel = db.Column(db.String(10), nullable=False)
    def __repr__(self):
        return f"<Paciente: {self.nombre} - DNI: {self.dni}>"

    class Turno(db.Model):
        __tablename__ = 'turno'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        fecha = db.Column(db.DateTime, nullable=False)
        dni = db.Column(db.BigInteger, db.ForeignKey('paciente.dni'), nullable=False)
        matricula = db.Column(db.BigInteger, db.ForeignKey('medico.matricula'), nullable=False)
        estado = db.Column(db.String(20), nullable=False) 

    class Medico(db.Model):
        __table__ = 'medico'
        matricula = db.column(db.integer, primary_key=True) 
        nombre = db.column(db.String(100), nullable=False)
        especialidad = db.column(db.String(100), nullable=False)
        tel = db.column(db.String(10), nullable=False)