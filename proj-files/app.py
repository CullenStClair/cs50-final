# Copyright Cullen St. Clair and Kamran Yaghoubian 2020

from tempfile import mkdtemp

from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.exceptions import (HTTPException, InternalServerError, default_exceptions)

# Configure Flask application
app = Flask(__name__)

# Ensure templates are auto-reloaded [from application.py in Finance]
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies) [from application.py in Finance]
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Default route
@app.route("/")
def index():
    return render_template("index.html")

# Handle InternalServerError (unexpected error) [from application.py in Finance]
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
        i = 4
    return "Internal Server Error 500"

# Listen for errors [from application.py in Finance]
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)