from flask import Flask, render_template,request, url_for, redirect, session, flash  
from flask_sqlalchemy import SQLAlchemy  
from werkzeug.security import generate_password_hash, check_password_hash  


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')


db = SQLAlchemy(app)
app.app_context().push()


class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), unique=True, nullable=False)
	email = db.Column(db.String(100), unique=True, nullable=False)
	password = db.Column(db.String(100), nullable=False)
	post = db.relationship('Post', backref='user', lazy=True)


	def __str__(self):
		return f"{self.username}, {self.email}"




class Post(db.Model):
	post_id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(200))
	content = db.Column(db.Text)
	author = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

@app.route('/')
def home():
	return render_template("home.html")



@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form.get('username')
		email = request.form.get('email')
		password = request.form.get('password')
		confirm_password = request.form.get('confirm_password')

		if password == confirm_password:
			hashed_password = generate_password_hash(password)
			user = User(username=username, email=email, password=hashed_password)
			db.session.add(user)
			db.session.commit()
			flash("Your account has been created")
			return redirect(url_for('login'))

	return render_template("register.html", title="Registeration Page")



@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		username = request.form.get("username")
		password = request.form.get("password")

		user = User.query.filter_by(username=username).first()
		if user and check_password_hash(user.password, password):
			session['user'] = user.user_id
			flash("Welcome " + user.username)
			return redirect(url_for('profile'))
	return render_template("login.html", title="Login Page")





@app.route('/logout')
def logout():
	if 'user' in session:
		session.pop('user', None)
		return redirect(url_for('login'))
	else:
		return redirect(url_for('login'))




@app.route('/profile')
def profile():
	if 'user' in session:
		return render_template("profile.html")
	else:
		return redirect(url_for('login'))



@app.route('/dashboard')
def dashboard():
	posts = Post.query.all()
	return render_template("dashboard.html", title="Dashboard", posts=posts)



@app.route('/post', methods=['GET', 'POST'])
def add_post():
	if 'user' in session:
		user = session['user']
		if request.method == 'POST':
			title = request.form.get('title')
			content = request.form.get('content')
			post = Post(title=title, content=content, author=user)
			db.session.add(post)
			db.session.commit()
			return redirect(url_for("dashboard"))
		return render_template("add_post.html", title="Add Post")
	else:
		return redirect(url_for('login'))




@app.route('/getpost/<int:post_id>')
def getpost(post_id):
	post = Post.query.filter_by(post_id=post_id).first()
	return render_template("one_post.html", post=post)



@app.route('/updatepost/<int:post_id>', methods=['GET', 'POST'])
def updatepost(post_id):
	if 'user' in session:
		post = Post.query.filter_by(post_id=post_id).first()
		if request.method == 'POST':
			post.title = request.form.get('title')
			post.content = request.form.get('content')
			db.session.commit()
			return redirect(url_for('getpost', post_id=post.post_id))

		return render_template("updatepost.html", post=post)
	else:
		return redirect(url_for('login'))



@app.route('/deletepost/<int:post_id>')
def deletepost(post_id):
	if 'user' in session:
		post = Post.query.filter_by(post_id=post_id).first()
		db.session.delete(post)
		db.session.commit()
		return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('login'))



