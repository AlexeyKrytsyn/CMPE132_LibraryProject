from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import *
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_bcrypt import Bcrypt

app = Flask(__name__)


#some commands for the database to work
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///libary.db'
app.config['SECRET_KEY'] = '3620deae109765e0eff33078'
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]='filesystem'
app.permanent_session_lifetime = timedelta(minutes = 5)



#Initalize the Database
db = SQLAlchemy(app)
migrate=Migrate(app,db)
bcrypt = Bcrypt(app)
Session(app)
BOOK_IMAGES= "static/images/"
app.config['UPLOAD_FOLDER'] = BOOK_IMAGES

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(255), nullable=False)
    lname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    edu = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default=0, nullable=False)
    def __repr__(self):
        return f'User("{self.id}", "{self.fname}", "{self.lname}", "{self.email}","{self.username}", "{self.edu}","{self.status}")'


#Librarian Class
class Librarian(db.Model):
    __tablename__='librarian'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(255), nullable=False)
    lname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    edu = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Integer, default=0, nullable=True)
    def __repr__(self):
        return '<Name %r>' %self.name
    
class LibForm(FlaskForm):
    fname= StringField("First Name", validators= [DataRequired()])
    lname= StringField("Last Name", validators= [DataRequired()])
    email= StringField("Email" , validators= [DataRequired()])
    edu= StringField("Position", validators= [DataRequired()])
    password= PasswordField("Password", validators= [DataRequired()])
    status= IntegerField("Status", [validators.optional(), NumberRange(min=0, max=1)])
    submit =SubmitField("Submit")

#create Admin class
class Admin(db.Model):
    __tablename__='Admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    def __repr__(self):
        return f'Admin("{self.edu}","{self.id}")'
    
# Creates book database
class Books(db.Model):
    __tablename__='books'
    id= db.Column(db.Integer,primary_key=True)
    name= db.Column(db.String(255),nullable=False,unique=True)
    genre= db.Column(db.Text,nullable=False)
    image_path=db.Column(db.String(),nullable=True)
    def __repr__(self):
        return '<Name %r>' %self.name

class bookForm(FlaskForm):
    name = StringField("Name", validators= [DataRequired()])
    genre =TextAreaField("Genre", [validators.optional(),validators.length(max=800)])
    image =FileField("Image")
    submit =SubmitField("Submit")

#creating the table of data
with app.app_context(): 
    db.create_all()

#insert admin data one time
with app.app_context(): 
    admin =Admin(username='alexeykrytsyn', password= bcrypt.generate_password_hash('alexeykrytsyn', 10))
    db.session.add(admin)
    db.session.commit()


#main index
#this the default page, and it goes to the main index file
@app.route('/')
def index():
    return render_template('index.html', title="")


#when typing in /admin/ in the searchbar it sends you to the admin_folder that holds index.html
@app.route('/admin/', methods=["POST", "GET"])
def adminIndex():
    if  session.get('admin_id'):
        return redirect('/admin/dashboard')
    #check the request is post or not
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username=="" and password=="":
            flash('please fill all the field', 'danger')
            return redirect('/admin/')
        else:
            admins=Admin.query.filter_by(username=username).first()
            
            if admins and bcrypt.check_password_hash(admins.password,password):
                session['admin_id'] = admins.id
                session['admin_name'] = admins.username
                flash('Login Success', 'success')
                return redirect('/admin/dashboard')
            else:
                flash('Invalid email and/or password', 'danger')
                return redirect('/admin/')
    #get the values of field
    else:
        return render_template('admin/index.html', title = "Admin Login")


@app.route('/admin/dashboard')
def adminDashboard():
    if not session.get('admin_id'):
        return redirect('/admin/')
    return render_template('/admin/dashboard.html', title="Admin Dashboard")

#admin get-all-users
@app.route('/admin/get-all-user', methods=["POST", "GET"])
def adminGetAllUser():
    users=User.query.all()
    return  render_template('admin/all-user.html', title='Approve User', users=users)

#approve users
@app.route('/admin/approve-user/<int:id>')
def adminApprove(id):
    User().query.filter_by(id=id).update(dict(status=1))
    db.session.commit()
    flash('Approve Success', 'success')
    return redirect('/admin/get-all-user')

#deleting users
@app.route('/admin/delete-user/<int:id>')
def adminDelete(id):
    if not session.get('admin_id'):
        flash('Unauthorized action. Please log in as admin.', 'danger')
        return redirect('/admin/')
    user = User.query.get(id)
    if user:
        try:
            db.session.delete(user)
            db.session.commit()
            flash(f'User "{user.username}" deleted successfully.', 'success')
        except Exception as e:
            flash('Error occurred while deleting user.', 'danger')
            db.session.rollback()
            print(str(e))
    else:
        flash('User not found.', 'warning')
    return redirect('/admin/get-all-user')

#admin Logout
@app.route('/admin/logout')
def adminLogout():
    if not session.get('admin_id'):
        return redirect('/admin/')
    if session.get('admin_id'):
        session['admin_id']=None
        session['admin_name']=None
        return redirect('/')
    
# Adds librarians
@app.route('/admin/add_Librarian',methods=['GET', 'POST'])
def add_Lib():
    email=None
    form=LibForm()
    if form.validate_on_submit():
        lib=Librarian.query.filter_by(email=form.email.data).first()
        if lib is None:
            lib=Librarian(fname=form.fname.data,
                        lname=form.lname.data,
                        email=form.email.data,
                        password= bcrypt.generate_password_hash(form.password.data, 10),
                        edu=form.edu.data,
                        status= form.status.data
                        )

            db.session.add(lib)
            db.session.commit()
        email=form.fname.data + ' ' +form.lname.data
        form.fname.data=''
        form.lname.data=''
        form.email.data=''
        form.password.data=''
        form.edu.data=''
        form.status.data=''
        flash(email +" Added Successfully")
    all_lib=Librarian.query.order_by(Librarian.id)
    return render_template('/admin/add_Librarian.html', form=form, all_lib=all_lib)

@app.route('/admin/update_Lib/<int:id>',methods=['GET','POST'])
def updateLib(id):
    form=LibForm()
    name_to_up=Librarian.query.get_or_404(id)
    if request.method =="POST":
        name_to_up.fname= request.form['fname']
        name_to_up.lname= request.form['lname']
        name_to_up.email= request.form['email']
        name_to_up.username= request.form['username']
        name_to_up.password= request.form['password']
        name_to_up.edu= request.form['edu']
        name_to_up.status= request.form['status']
        try:
            db.session.commit()
            flash ("Updated Successfully")
            return redirect(url_for('updateLib', id=id))
        except:
            flash("Error")
            return redirect(url_for('updateLib', id=id))
    else:
        flash("Error")
        return render_template("/admin/update_Lib.html", form=form, name_to_up=name_to_up , id=id)

@app.route('/admin/add_Librarian/librarian_del/<int:id>')
def delLib(id):
    lib_to_del=  Librarian.query.get_or_404(id)
    name=None
    form=LibForm()
    try:
        db.session.delete(lib_to_del)
        db.session.commit()
        flash("Librarian Deleted Successfully")
        all_lib= Librarian.query.order_by(Librarian.id)
        return redirect('/admin/add_Librarian')
    
    except:
        flash(" Error unable to delet user")
        return redirect('/admin/add_Librarian') 


# ----------------------------------------Libraian area of code-----------------------------------------

#when typing in /admin/ in the searchbar it sends you to the admin_folder that holds index.html

#!!!!! is using email instead of Username
@app.route('/Librarian/', methods=["POST", "GET"])
def librianIndex():
    if  session.get('Librian_id'):
        return redirect('/Librarian/dashboard.html')
    #check the request is post or not
    if request.method=='POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email=="" and password=="":
            flash('please fill all the field', 'danger')
            return redirect('/Librian/')
        else:
            Librarians=Librarian.query.order_by(Librarian.email).first()
            
            if Librarians and bcrypt.check_password_hash(Librarians.password,password):
                session['Librarian_id'] = Librarians.id
                session['Librarian_email'] = Librarians.email
                flash('Login Success', 'success')
                return render_template('/Librarian/dashboard.html')
            else:
                flash('Invalid email and/or password', 'danger')
                return render_template('/Librarian/index.html')
    #get the values of field
    else:
        return render_template('Librarian/index.html', title = "Librarian Login")

    
@app.route('/Librarian/add_del_books',methods=['GET', 'POST'])
def add_book():
    name=None
    form=bookForm()
    if form.validate_on_submit():
        book=Books.query.filter_by(name=form.name.data).first()
        if book is None:
            book=Books(name=form.name.data,
                        genre=form.genre.data)
            db.session.add(book)
            db.session.commit()
        name=form.name.data
        form.name.data=''
        form.genre.data=''
        flash("Book Added Successfully")
    all_books=Books.query.order_by(Books.id)
    return render_template('/Librarian/add_del_books.html', form=form, all_books=all_books)


@app.route('/Librarian/booklist')
def booklistLib():
    all_books=Books.query.order_by(Books.id.desc())
    return render_template('Librarian/booklist.html', all_books=all_books)

# #Update book record
@app.route('/Librarian/book_update/<int:id>',methods=['GET','POST'])
def updateBook(id):
    form=bookForm()
    name_to_up=Books.query.get_or_404(id)
    if request.method =="POST":
        name_to_up.name= request.form['name']
        name_to_up.genre= request.form['genre']
        name_to_up.image= request.form['image']
        try:
            db.session.commit()
            flash ("Updated Successfully")
            return redirect(url_for('updateBook', id=id))
        except:
            flash("Error")
            return redirect(url_for('updateBook', id=id))
    else:
        flash("Error")
        return render_template("/Librarian/book_update.html", form=form, name_to_up=name_to_up , id=id)
        
@app.route('/Librarian/add__del_books/book_del/<int:id>')
def delBook(id):
    lib_to_del=  Books.query.get_or_404(id)
    name=None
    form=bookForm()
    try:
        db.session.delete(lib_to_del)
        db.session.commit()
        flash("Book Deleted Successfully")
        all_lib= Books.query.order_by(Books.id)
        return redirect('booklistLib')
    
    except:
        flash(" Error unable to delet user")
        return redirect('booklistLib') 







# ----------------------------------------Libraian area of code-----------------------------------------


# ----------------------------------------user area of code-----------------------------------------

#Has the route to the book list 
@app.route('/user/booklist')
def booklist():
    all_books=Books.query.order_by(Books.id.desc())
    return render_template('user/booklist.html', all_books=all_books)

# For adding books to db

    
    



#when typing in /user/ in the searchbar it sends you to the user_folder that holds index.html
@app.route('/user/', methods=['POST', 'GET'])
def userIndex():
    #allows live sessions and whenlogged you stayed logged in as the user
    if  session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=="POST":
        # get the name of the field
        session.permanent == True
        email=request.form.get('email')
        password=request.form.get('password')
        # check user exist in this email or not
        users=User.query.filter_by(email=email).first()
        if users and bcrypt.check_password_hash(users.password,password):
            # check the admin approve your account are not
            is_approve=User.query.filter_by(id=users.id).first()
            # first return the is_approve:
            if is_approve.status == 0:
                flash('Your Account is not approved by Admin','danger')
                return redirect('/user/')
            else:
                session['user_id']=users.id
                session['username']=users.username
                flash('Login Successfully','success')
                return redirect('/user/dashboard')
        else:
            flash('Invalid Email and Password','danger')
            return redirect('/user/')
    else:
        return render_template('user/index.html',title="User Login")

#when typing in /user/signup in the searchbar it sends you to the user_folder that holds signup.html
@app.route('/user/signup', methods=['POST', 'GET'])
def userSignup():
    if session.get('user_id'):
        return redirect('/user/dashboard')
    if request.method=='POST':
#get all input field names/information
        fname=request.form.get('fname')
        lname=request.form.get('lname')
        email=request.form.get('email')
        username=request.form.get('username')
        edu=request.form.get('edu')
        password=request.form.get('password')

#checks all the fields are filled out and are not empty
        if fname =="" or lname=="" or email=="" or username=="" or password =="" or edu=="":
            flash('Please fill all the fields to register' , 'danger')
            return redirect('/user/signup')
        else:
            is_email=User().query.filter_by(email=email).first()
            if is_email:
                flash('Email already exists', 'danger')
                return redirect('/user/signup')
            hash_password = bcrypt.generate_password_hash(password, 10)
            user = User(fname = fname, lname=lname, email=email, password=hash_password, edu=edu, username=username)
            db.session.add(user)
            db.session.commit()
            flash('Account Created, waiting for admin approval......', 'success')
            return redirect('/user/')
    else:
        return render_template('user/signup.html', title = "User Signup")



# user dashboard
@app.route('/user/dashboard')
def userDashboard():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        id=session.get('user_id')
    users=User().query.filter_by(id=id).first()
    return render_template('user/dashboard.html',title="User Dashboard",users=users)

#user logout
@app.route('/user/logout')
def userLogout():
    if not session.get('user_id'):
        return redirect('/user/')
    if session.get('user_id'):
        session['user_id'] = None
        session['username'] = None
        return redirect('/user/')


if __name__ == "__main__":
    app.run(debug = True)
