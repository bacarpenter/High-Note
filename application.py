#These setup lines come from finance on the web track and they may have been changed
import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import login_required
import random

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Open the database
db = SQL("sqlite:///lessAlone.db")

@app.route("/")
@login_required
def index():
    note = db.execute("SELECT * FROM messages ORDER BY random() LIMIT 25")
    i = 0
    while i < len(note):
        note[i]['username'] = db.execute("SELECT username FROM users WHERE user_id = :user_id", user_id=note[i]['user_id'])[0]['username']
        i += 1

    return render_template("index.html", note=note, noteLen=len(note))

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in (this was based on the login from web/finance)"""
    session.clear()

    if request.method == "POST":
        # Get info from the data base on given username:
        user = db.execute("SELECT * FROM users WHERE username = :username", username = request.form.get("username"))

        # Make sure user is in the database and password matches:
        if not user or not check_password_hash(user[0]['password'], request.form.get("password")):
            return apology("incorrect username / password")

        else:
            session['user_id'] = user[0]['user_id']
            newUser = db.execute("SELECT welcomed FROM users WHERE user_id = :user_id", user_id = session['user_id'])
            if newUser[0]['welcomed'] == 0:
                return redirect("/welcome")

            else:
                return redirect("/")


    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user (this was based on the login from web/finance)"""
    session.clear()
    print(session)
    if request.method=="POST": #If user is submitting the form

        #Check passowrds match
        if request.form.get("password") != request.form.get("passwordConfirm"):
            return apology("Passwords do not match")

        # Ensure username was submitted and is unique in the db (coppied and editedfrom login and the distro code)
        if not request.form.get("username"):
            return apology("you must provide username")

        rowsReg = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if len(rowsReg) != 0:
            return apology("Username taken")

        # Ensure password was submitted (coppied from login and the distro code)
        elif not request.form.get("password"):
            return apology("must provide password")

        pHash = generate_password_hash(request.form.get("password"))
        # Insert user into db
        insertRow = db.execute("INSERT INTO users (username, password) VALUES (:username, :pHash)", username=request.form.get("username"), pHash=pHash)
        return redirect("/login")

    else:
        return render_template("register.html")

@app.route("/compose", methods = ["GET", "POST"])
@login_required
def compose():
    """Allow users to write their notes """
    if request.method == "POST":
        #Insert note into the data base:
        print(request.form.get("signed"))
        if request.form.get("signed") == "on":
            signed = 1
        else:
            signed = 0

        message = db.execute("INSERT INTO messages (message_text, user_id, signed) VALUES (:body, :user_id, :signed)", body = request.form.get("body"), user_id = session['user_id'], signed = signed)
        return render_template("noteConformation.html")

    else:
        return render_template("compose.html")

@app.route("/logout")
def logout():
    session.clear()
    print(session)
    return redirect("/")

@app.route("/welcome")
@login_required
def welcome():
    db.execute("UPDATE users SET welcomed = 1 WHERE user_id = :user_id", user_id=session['user_id'])
    print(f"user #{session['user_id']} has been welcomed")
    return render_template("welcome.html")
@app.route("/report", methods = ["GET", "POST"])
@login_required
def report():
    if request.method == "POST":

        # Make sure that the message_id is valid
        if not db.execute("SELECT * FROM messages WHERE message_id = :message_id", message_id=request.form.get("message_id")):
            return apology("Message id is not vaild.")

        db.execute("INSERT INTO reports (message_id, user_id, reason) VALUES (:message_id, :user_id, :reason)", message_id=request.form.get("message_id"), user_id=session['user_id'], reason=request.form.get("reason"))
        return render_template("reportConformation.html")

    else:
        return render_template("report.html")

def apology(message):
    print (message)
    message = message
    return render_template("apology.html", message=message)


""" Note, I took code from both the distrotbution and my own code from finance on the web track
With all my love going to Brady and my family <3"""