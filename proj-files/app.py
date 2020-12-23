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
        session['traits_dom'] = []
        session['traits_rec'] = []

        # ensures all fields are full
        for i in range(count):
            if (not request.form.get(f'dominant{i}')) or (not request.form.get(f'recessive{i}')):
                return error("Bad request: Missing trait.", 400)
            else:
                # adds traits to their respective lists
                session['traits_dom'].append(request.form.get(f'dominant{i}'))
                session['traits_rec'].append(request.form.get(f'recessive{i}'))
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
        parent1 = []
        parent2 = []
        for i in range(session['count']):
            # checks which traits are homo dom, homo rec, or hetero for parent 1
            if request.form.get(f'p1t{i}') == 'hr':
                parent1.append('hr')
            elif request.form.get(f'p1t{i}') == 'he':
                parent1.append('he')
            elif request.form.get(f'p1t{i}') == 'hd':
                parent1.append('hd')
            # checks which traits are homo dom, homo rec, or hetero for parent 2
            if request.form.get(f'p2t{i}') == 'hr':
                parent2.append('hr')
            elif request.form.get(f'p2t{i}') == 'he':
                parent2.append('he')
            elif request.form.get(f'p2t{i}') == 'hd':
                parent2.append('hd')
        return render_template("check.html", stuff=request.form.get("p1t1"))

# Handle InternalServerError (unexpected error) [from application.py in Finance]
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error("Internal Server Error", 500)

# Listen for errors [from application.py in Finance]
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
