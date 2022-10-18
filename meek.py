from flask import Flask,render_template,request, url_for,redirect
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length 
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime


app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///post.db'
app.config['SECRET_KEY'] = '5b4319099f89474385b2fb8d'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(UserMixin,db.Model):
	id=db.Column(db.Integer, primary_key=True)
	username=db.Column(db.String(20),nullable=False,unique=True)
	email=db.Column(db.String(50),nullable=False,unique=True)
	password=db.Column(db.String(80),nullable=False)
	


class Pundit(db.Model):
	id=db.Column(db.Integer, primary_key=True)
	title=db.Column(db.String(100), nullable=False)
	content=db.Column(db.Text,nullable=False)
	author=db.Column(db.String(20),nullable=False,default="N/A")
	date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
		
	def __repr__(self):
		return 'Pundit ' + str(self.id)
		
		
class LoginForm(FlaskForm):
	username = StringField(label="username",validators=[Length(min=4,max=15),DataRequired()])
	password = PasswordField(label="password",validators=[Length(min=8,max=80),DataRequired()])
	submit = SubmitField(label="signup")



			
		
class SignupForm(FlaskForm):
	username = StringField(validators=[Length(min=4,max=30),DataRequired()])
	email = StringField(validators=[Email(),DataRequired()])
	password = PasswordField(validators=[Length(min=6),DataRequired()])
	submit = SubmitField()
		

	

@app.route("/")
@app.route("/login",methods=["GET","POST"])
def login():
	form = LoginForm()
	user = User.query.filter_by(username=form.username.data).first()
	if user:
		if check_password_hash(user.password, form.password.data):
			login_user(user)
			
			return redirect("/posts")
	return render_template("login.html", form=form)

    
    
    
@app.route("/signup",methods=["GET","POST"])
def signup():
	form = SignupForm()
	if form.validate_on_submit():
		new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
		db.session.add(new_user)
		db.session.commit()
		return redirect("/login")
		if form.errors != {} :
			for err_msg in form.errors.values():
				print(f'there was an error in creating user:{err_msg}')
		
		
	return render_template("signup.html",form=form)
	

    
    
@app.route("/posts", methods=["GET","POST"]) 
def posts():
	if request.method== "POST":
		post_title= request.form["title"]
		post_content= request.form["content"]
		post_author= request.form["author"]
		new_post= Pundit(title=post_title, content=post_content,author=post_author)
		db.session.add(new_post)
		db.session.commit()
		return redirect("/posts")
	
	else:
		all_posts = Pundit.query.order_by(Pundit.date_posted).all()
		return render_template("posts.html",posts=all_posts)  
		
		
@app.route("/posts/delete/<int:id>") 
def delete(id):
	post= Pundit.query.get_or_404(id)
	db.session.delete(post)
	db.session.commit()
	return redirect("/posts")

@app.route("/posts/edit/<int:id>", methods=["GET","POST"]) 
def edit(id):
	post= Pundit.query.get_or_404(id)
	if request.method=="POST":
		post.title = request.form["title"]
		post.author = request.form["author"]
		post.content = request.form["content"]
		db.session.commit()
		return redirect("/posts")
	else:
		return render_template("edit.html",post=post)
 


@app.route('/create')
def create():
    db.create_all()
    return 'All tables created'	


	
	
    
	    
if __name__ == "__main__" : 
   app.run(debug = True)


