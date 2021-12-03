import pdfkit

from flask.helpers import flash

import sqlalchemy
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template,request, session,escape, redirect, url_for,flash, make_response




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost/flask2"
app.secret_key='mysecretkey'
#conection=app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost/flask2"
db = SQLAlchemy(app)





class Teacher(db.Model):
    id =db.Column(db.Integer,primary_key=True,nullable=False,)
    username= db.Column(db.String(80), unique=False, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=False,nullable=False)
    

    def __init__(self,username,email,password):
        self.username=username
        self.email=email
        self.password=password
    def __repr__(self):
        return '<User %r>' % self.username


class Student(db.Model):
    id =db.Column(db.Integer,primary_key=True, nullable=False)
    teacher = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    name= db.Column(db.String(80), unique=False, nullable=False)
    lastname=db.Column(db.String(80), unique=False, nullable=False)
    email=db.Column(db.String(120), unique=True, nullable=False)
    
    def __init__(self,name,lastname,email,teacher):
        
        self.name=name
        self.lastname=lastname
        self.email=email
        
        self.teacher=teacher
    def __repr__(self):
        return f'Student({self.name},{self.lastname},{self.email})'

    def __str__(self):
        return self.name
    

class Signatures_first_year(db.Model):
    __table_args__ = (
        db.UniqueConstraint('trimester', 'student'),
    )
    id = db.Column(db.Integer, primary_key=True)
    trimester = db.Column(db.Integer,nullable=False,unique=False)
    teacher = db.Column(db.Integer, db.ForeignKey('teacher.id',ondelete='CASCADE'), nullable=False)
    student = db.Column(db.Integer, db.ForeignKey('student.id',ondelete='CASCADE'), nullable=False,unique=False)
    español= db.Column(db.Float)
    matematicas=db.Column(db.Float)
    educacion_fisica=db.Column(db.Float)
    artes= db.Column(db.Float)
    conocimiento_del_medio=db.Column(db.Float)
    vida_saludable=db.Column(db.Float)
    formacion_civica=db.Column(db.Float)

  

    def __init__(self,trimester,teacher,student,español,matematicas,educacion_fisica,artes,conocimiento_del_medio,vida_saludable,formacion_civica):
        self.trimester=trimester
        self.teacher=teacher
        self.student=student
        self.español=español
        self.matematicas=matematicas
        self.educacion_fisica=educacion_fisica
        self.artes=artes
        self.conocimiento_del_medio=conocimiento_del_medio
        self.vida_saludable=vida_saludable
        self.formacion_civica=formacion_civica
    
    def __str__(self):
        return self.id
    
    def __repr__(self):
        return '<User %r>' % self.student












@app.route('/')
def index():
    if "id" in session and "username" in session:
        teacher_id = session["id"]
        teacher_name = session["username"]
        
        
        datas = Student.query.filter_by(teacher=teacher_id).all()
        #print(datas)
        return render_template('index.html', studentone=datas,teacher_name=teacher_name)
    return redirect(url_for("login"))
    
    

    
@app.route('/add_contact', methods=['POST'])
def add_contact():
    try:
        if request.method == 'POST':
            name = request.form['name']
            lastname=request.form['lastname']
            email = request.form['email']
           
            teacher = session["id"]
            data=Student(name,lastname,email,teacher)

            db.session.add(data)
            db.session.commit()
            flash('Alumno agregado')
            return redirect(url_for('index'))
    except:
        flash("El alumno ya está registrado")
    return redirect(url_for('index'))




@app.route('/delete/<string:id>')
def delete_student(id):
    if "id" in session:
        student= Student.query.get(id)
        db.session.delete(student)
        db.session.commit()
        flash('Alumno eliminado de la base de datos')
        return redirect(url_for('index'))
    return redirect(url_for('login'))




@app.route('/update/<id>',methods = ['POST'])
def update_contact(id):
    if "id" in session:
        if request.method == 'POST':
            
            study= db.session.query(Student).filter(Student.id==id).first()

            study.name= request.form['name']
            study.lastname=request.form['lastname']
            study.email = request.form['email']
            study.qualification = request.form['qualification']
            study.coments=request.form['coments']
            db.session.commit()
            return redirect(url_for('index'))
    return redirect(url_for('login'))




@app.route('/edit/<id>')
def edit_student(id):
    if "id" in session:
        ob = db.session.query(Student).get(id)
        return render_template('edit_student.html',student=ob)
    return redirect(url_for('login'))




@app.route("/signup", methods = ["GET","POST"])
def signup():
    if "id" in session:
        return redirect(url_for('index'))
    try:
        if request.method == "POST":
            hashed_pw = generate_password_hash(request.form["password"], method ="sha256")
            new_user = Teacher(username = request.form["username"], email = request.form['email'], password=hashed_pw)
        
            db.session.add(new_user)
            db.session.commit()
            flash("You've registered succesfuly","success")

            return redirect(url_for("login"))
    except:
        flash("El usuario ya existe")
    return render_template("signup.html")




@app.route("/login", methods=["GET","POST"])
def login(): 
    if "id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        user = Teacher.query.filter_by(email= request.form["email"]).first()
        if user and check_password_hash( user.password,request.form["password"]):
            session["id"] = user.id
            session["username"]= user.username
            return redirect(url_for("index"))
        flash( "Your credentials are invalid, check try again","error")
    return render_template("login.html")




@app.route("/logout")
def logout():
    
    session.pop("id", None)
    flash("You are logged out.","error")
    return redirect(url_for("login"))



@app.route('/addnotes/<id>', methods = ['POST','GET'])
def add_notes(id):
    if "id" in session:
        student=Student.query.filter_by(id=id).all()
        data_student=Signatures_first_year.query.filter_by(student=id).all()
        prom_signature = Signatures_first_year.query.with_entities(
        func.round(func.avg(Signatures_first_year.español)),
        func.round(func.avg(Signatures_first_year.matematicas)),
        func.round(func.avg(Signatures_first_year.artes)),
        func.round(func.avg(Signatures_first_year.vida_saludable)),
        func.round(func.avg(Signatures_first_year.conocimiento_del_medio)),
        func.round(func.avg(Signatures_first_year.formacion_civica)),
        func.round(func.avg(Signatures_first_year.educacion_fisica))
        ).filter(Signatures_first_year.student==id).all()
        try:
            finalprom = sum(prom_signature[0])/len(prom_signature[0])
        #print(finalprom)
        except:
            finalprom = 0.0
        


        return render_template("note_add.html", student=student,data_student=data_student, prom_signature=prom_signature,finalprom=finalprom )
    
    return redirect(url_for("login"))

@app.route('/savenotes/<id>', methods = ['POST'])
def save_notes(id):
    if "id" in session:
        try:
            trimester = request.form['trimester']
            español= request.form['español']
            matematicas = request.form['matematicas']
            artes = request.form['artes']
            vida_saludable = request.form['vidasal']
            conocimiento_del_medio = request.form['conocimiento']
            formacion_civica = request.form['formacion']
            educacion_fisica = request.form['educacion']
            student=id
                
                
            data = Signatures_first_year(teacher=int(session["id"]),student=student,español=español,matematicas=matematicas,artes=artes,vida_saludable=vida_saludable,conocimiento_del_medio=conocimiento_del_medio,formacion_civica=formacion_civica,educacion_fisica=educacion_fisica,trimester=trimester)
            db.session.add(data)
            db.session.commit()
        
        except sqlalchemy.exc.IntegrityError:
        
            flash('El Alumno ya fué calificado en el trimestre seleccionado')
        except sqlalchemy.exc.DataError:
            flash('Asegurate de rellenar todos los campos requeridos')
        return redirect(url_for('add_notes',id=id))
    return redirect(url_for('login'))




@app.route('/editnotes/<id>/<student>', methods=["POST","GET"])
def edit_notes(id,student):
    if "id" in session:
        ob = db.session.query(Signatures_first_year).get(id)
        student = db.session.query(Signatures_first_year).get(student)
        return render_template('edit_notes.html',signature=ob, student=student)
    return redirect(url_for('login'))


@app.route('/updatescore/<id>/<student>',methods = ['POST', "GET"])
def update_score(id,student):
    if "id" in session:
        if request.method == 'POST':
            try:
                study= db.session.query(Signatures_first_year).filter(Signatures_first_year.id==id).first()
                study.student = student
                study.trimester= request.form['trimester']
                study.español=request.form['español']
                study.matematicas = request.form['matematicas']
                study.artes = request.form['artes']
                study.vida_saludable=request.form['vidasal']
                study.conocimiento_del_medio= request.form['conocimiento']
                study.formacion_civica= request.form['formacion']
                study.educacion_fisica = request.form['educacion']
            
                db.session.commit()


            except sqlalchemy.exc.IntegrityError:
            
                flash('El Alumno ya fué calificado en el trimestre seleccionado')
                return redirect(url_for('edit_notes',id=id, student=student))
            except sqlalchemy.exc.DataError:
                flash('Asegurate de rellenar todos los campos requeridos')
                return redirect(url_for('edit_notes',id=id, student=student))
            return redirect(url_for('add_notes',id=student))

    return redirect(url_for("login"))




@app.route('/deletenote/<string:id>/<student>')
def delete_note(id,student):
    if "id" in session:
        signatures= Signatures_first_year.query.get(id)
        
        db.session.delete(signatures)
        db.session.commit()
        flash('notas eliminadas')
        return redirect(url_for('add_notes',id=student))
    return redirect(url_for('login'))



@app.route('/shownotes/<id>', methods = ['POST','GET'])
def show_notes(id):
   
    student=Student.query.filter_by(id=id).all()
    for s in student:
        if s in student:
            data_student=Signatures_first_year.query.filter_by(student=id).all()
            prom_signature = Signatures_first_year.query.with_entities(
            func.round(func.avg(Signatures_first_year.español)),
            func.round(func.avg(Signatures_first_year.matematicas)),
            func.round(func.avg(Signatures_first_year.artes)),
            func.round(func.avg(Signatures_first_year.vida_saludable)),
            func.round(func.avg(Signatures_first_year.conocimiento_del_medio)),
            func.round(func.avg(Signatures_first_year.formacion_civica)),
            func.round(func.avg(Signatures_first_year.educacion_fisica))
            ).filter(Signatures_first_year.student==id).all()
            try:
                finalprom = sum(prom_signature[0])/len(prom_signature[0])
                #print(finalprom)
            except:
                finalprom = 0.0
                


            return render_template("shownotes.html", student=student,data_student=data_student, prom_signature=prom_signature,finalprom=finalprom )
    flash('Alumno no registrado')
    return redirect(url_for('findstudent'))
    





@app.route('/findstudent/', methods=['GET','POST'])
def findstudent():
    if request.method == 'POST':
        student=request.form['id']
        
        return redirect(url_for('show_notes', id=student))
       
    return render_template('find_student.html')



@app.route('/downlandpdf/<id>', methods = ['POST','GET'])
def downlandpdf(id):
    if request.method == 'GET':
        student=Student.query.filter_by(id=id).all()
        data_student=Signatures_first_year.query.filter_by(student=id).all()
        prom_signature = Signatures_first_year.query.with_entities(
        func.round(func.avg(Signatures_first_year.español)),
        func.round(func.avg(Signatures_first_year.matematicas)),
        func.round(func.avg(Signatures_first_year.artes)),
        func.round(func.avg(Signatures_first_year.vida_saludable)),
        func.round(func.avg(Signatures_first_year.conocimiento_del_medio)),
        func.round(func.avg(Signatures_first_year.formacion_civica)),
        func.round(func.avg(Signatures_first_year.educacion_fisica))
        ).filter(Signatures_first_year.student==id).all()
        try:
            finalprom = sum(prom_signature[0])/len(prom_signature[0])
            #print(finalprom)
        except:
            finalprom = 0.0
            
        

        #rendered1 =  redirect(url_for('show_notes',id=id))
        rendered =  render_template("boleta.html", student=student,data_student=data_student, prom_signature=prom_signature,finalprom=finalprom )
        css = 'static/bootstrap.css'
        
        pdf = pdfkit.from_string(rendered, False,   )
        
        response = make_response(pdf)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = "attachment; filename=output.pdf"
        return response 
    
    return redirect(url_for('show_notes',id=id))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=5000)
