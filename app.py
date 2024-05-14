from flask import Flask
from flask import render_template, redirect, request, session, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from os import getenv, urandom
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
	result = db.session.execute(text("SELECT content FROM messages"))
	messages = result.fetchall()
	contents = []
	for i in messages:
		contents.append(i.content)
	return render_template("index.html", contents = contents)

#FLAW 4
@app.route("/surprise<session_token>", methods = ["POST"])
#FLAW 4 Solution
#@app.route("/surprise", methods = ["POST"])

def surprise(session_token):
	name = request.form["name"]
	### FLAW 2
	return "Surprise!" + name
	### FLAW 2 Solution
	#return render_template("surprise.html", name = name)

@app.route("/send", methods = ["POST"])
def send():
	#FLAW 3 Solution
	#check_user()
	content = request.form["content"]
	###FLAW 1
	db.session.execute(text("INSERT INTO messages (content) VALUES ( '" + content + "')"))
	
	### FLAW 1 Solution
	#sql = "INSERT INTO messages (content) VALUES (:content)"
	#db.session.execute(text(sql), {"content" : content})
	
	db.session.commit()

	result = db.session.execute(text("SELECT content FROM messages"))
	messages = result.fetchall()
	contents = []
	for i in messages:
		contents.append(i.content)

	return contents.__iter__()

	#FLAW 2 Solution
	#return redirect("/")


@app.route("/login", methods = ["POST", "GET"])
def login():
	username = request.form["username"]
	password = request.form["password"]

	###FLAW 1
	result = db.session.execute(text("SELECT id, password FROM users WHERE username= '" + username +"'"))

	## FLAW 1 & FLAW 5 Solution
	#sql = "SELECT id, password, is_admin FROM users WHERE username=:username"
	#result = db.session.execute(text(sql), {"username":username})

	user = result.fetchone()
	

	if not user:

		###FLAW1
		db.session.execute(text("INSERT INTO users (username, password) VALUES('"+ username +"', '" + password + "')"))
		
		#FLAW 1 Solution
		#sql = "INSERT INTO users (username, password) VALUES(username, password)"
		#db.session.execute(text(sql), {"usernmae" : username, "password" : password})

		db.session.commit()
		session["username"] = username
		session["csrf_token"] = urandom(16).hex()
		session["session_token"] = urandom(16).hex()

		# FLAW 5
		#hash_value = generate_password_hash(password)
		#sql = "INSERT INTO users (username, password) VALUES(:usernmae, :password)"
		#db.session.execute(text(sql), {"usernmae" : username, "password" : hash_value})
	
	else:
		if user.password != password:
			return "Väärä salasana"
		session["username"] = username
		session["csrf_token"] = urandom(16).hex()
		session["session_token"] = urandom(16).hex()
		
	# FLAW 5
	if username == "admin" and password == "admin":
		session["is_admin"] = True
	
	# FLAW 5 Solution
		#if user.is_admin == "True":
		#	session["is_admin"] = True

	
	return redirect("/")

@app.route("/logout")
def logout():
	del session["username"]
	del session["session_token"]

	#FLAW 3 Solution
	#del session["csrf_token"]
	
	return redirect("/")

#FLAW 3 Solution
#def check_user():
#	if session["csrf_token"] != request.form["csrf_token"]:
#		abort(403)



