from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Adproff/Desktop/Prog/python/instance/clinica.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Paciente(db.Model):
    __tablename__ = 'paciente'
    id = db.Column(db.Integer, primary_key=True)
    nombre_paciente = db.Column(db.String(100), nullable=False)
    nombre_medico = db.Column(db.String(100), nullable=False)
    fecha_turno = db.Column(db.String(100))
    def __repr__(self):
        return f"<Paciente {self.nombre_paciente}- Médico: {self.nombre_medico}>"

@app.route('/')
def index():
    pacientes = Paciente.query.all()
    #print("index ",pacientes)
    return render_template('/index.html', pacientes=pacientes)

@app.route('/vistap')
def ver_pacientes():
    pacientes = Paciente.query.all()
    print("pacientes ce mamo ")
    return render_template('/vistap.html', pacientes=pacientes)    

@app.route('/add', methods=['POST'])
def add():
    nombre_paciente = request.form['nombre_paciente']
    nombre_medico = request.form['nombre_medico'] 
    fecha_turno = request.form['fecha_turno']   
    nuevo_paciente = Paciente(nombre_paciente=nombre_paciente, 
                              nombre_medico=nombre_medico, 
                              fecha_turno=fecha_turno)  # <-- corregido
    db.session.add(nuevo_paciente)  
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    paciente = Paciente.query.get_or_404(id)
    if request.method == 'POST':
        paciente.nombre_paciente = request.form['nombre_paciente']
        paciente.nombre_medico = request.form['nombre_medico'] 
        paciente.fecha_turno = request.form['fecha_turno']  # <-- corregido
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', paciente=paciente)  # <-- corregido


@app.route('/delete/<int:id>')
def delete(id):
    paciente = Paciente.query.get_or_404(id)
    db.session.delete(paciente)  # <-- corregido
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)