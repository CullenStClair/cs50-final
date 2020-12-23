# Copyright Cullen St. Clair and Kamran Yaghoubian 2020

from tempfile import mkdtemp

from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.exceptions import (HTTPException, InternalServerError, default_exceptions)

from helpers import error

# Configure Flask application
app = Flask(__name__)

# Ensure templates are auto-reloaded [from application.py in Finance]
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached [from application.py in Finance]
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies) [from application.py in Finance]
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Default route
@app.route("/", methods=["GET", "POST"])
def index():
    # checks if request method is get or post
    if request.method == "GET":
        return render_template("index.html")
    else:
        # gets number of traits and puts into session
        if not request.form.get('num'):
            return error("Bad request: Please enter a number of genes.", 400)
        count = int(request.form.get('num'))
        session['count'] = count
        
        # checks for number higher than 0
        if count <= 0:
            return error("Forbidden: Invalid number of genes.", 403)
        
        # pass count to genes page, redirect
        return redirect("/genes")

# Route where user inputs traits
@app.route("/genes", methods=["GET", "POST"])
def genes():
    # check if count is not set (user came here directly)
    try:
        session['count']
    except KeyError:
        return error("Bad request: Start at the beginning.", 400)

    # retrieve count
    count = session['count']

    # checks if request method is get or post
    if request.method == "GET":
        # render page, dynamic form size logic in genes.html
        return render_template("genes.html", count=count)
    else:
        # sets blank lists of dominant and recessive traits in session
        session['traits'] = [{}]

        # ensures all proper usage of fields
        for i in range(count):
            if (not request.form.get(f'dominant{i}')) or (not request.form.get(f'recessive{i}')):
                return error("Bad request: Missing trait.", 400)
            elif not request.form.get(f'symbol{i}'):
                return error("Bad request: Missing symbol.", 400)
            else:
                # adds traits to their respective lists
                session['traits'][i]['dom_n'] = request.form.get(f'dominant{i}')
                session['traits'][i]['dom_s'] = request.form.get(f'symbol_dom{i}')
                session['traits'][i]['rec_n'] = request.form.get(f'recessive{i}')
                session['traits'][i]['rec_s'] = request.form.get(f'symbol_rec{i}')

        return redirect("/parents")

@app.route("/parents", methods=["GET", "POST"])
def parents():
    # checks for method
    if request.method == "GET":
        # check if count is not set (user came here directly)
        try:
            session['count']
        except KeyError:
            return error("Bad request: Start at the beginning.", 400)
        return render_template("parents.html", count=session['count'])
    else:
        # check notes
        session['parents'] = [{}]
        for i in range(session['count']):
            # checks which traits are homo dom, homo rec, or hetero for parents
            session['parents'][i]['p1'] = request.form.get(f'p1t{i}')
            session['parents'][i]['p2'] = request.form.get(f'p2t{i}')

        return error("Unimplemented", 501)

# Handle InternalServerError (unexpected error) [from application.py in Finance]
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error("Internal Server Error", 500)

# Listen for errors [from application.py in Finance]
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
