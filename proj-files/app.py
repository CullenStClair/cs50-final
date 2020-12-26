# Copyright Cullen St. Clair and Kamran Yaghoubian 2020

from decimal import *
from tempfile import mkdtemp
import json

from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.exceptions import (HTTPException, InternalServerError, default_exceptions)

from helpers import *

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
@count_required
def genes():
    # retrieve count
    count = session['count']

    # checks if request method is get or post
    if request.method == "GET":
        # render page, dynamic form size logic in genes.html
        return render_template("genes.html", count=count)
    else:
        # sets blank lists of dominant and recessive traits in session
        session['traits'] = [{}]

        # ensure proper usage of all fields\
        for i in range(count):
            if (not request.form.get(f'dominant{i}')) or (not request.form.get(f'recessive{i}')):
                return error("Bad request: Missing trait.", 400)
            elif (not request.form.get(f'symbol_dom{i}')) or (not request.form.get(f'symbol_rec{i}')):
                return error("Bad request: Missing symbol.", 400)
            else:
                # adds traits to their respective lists
                if i > 25:
                    session['traits'].append({
                            'dom_n': request.form.get(f'dominant{i}'),
                            'dom_s': request.form.get(f'symbol_dom{i}') + str(i - 25),
                            'rec_n': request.form.get(f'recessive{i}'),
                            'rec_s': request.form.get(f'symbol_rec{i}') + str(i - 25)
                        })
                else:
                    if not len(session['traits'][0]):
                        session['traits'][0]['dom_n'] = request.form.get('dominant0')
                        session['traits'][0]['dom_s'] = request.form.get('symbol_dom0')
                        session['traits'][0]['rec_n'] = request.form.get('recessive0')
                        session['traits'][0]['rec_s'] = request.form.get('symbol_rec0')
                    else:
                        session['traits'].append({
                            'dom_n': request.form.get(f'dominant{i}'),
                            'dom_s': request.form.get(f'symbol_dom{i}'),
                            'rec_n': request.form.get(f'recessive{i}'),
                            'rec_s': request.form.get(f'symbol_rec{i}')
                        })
        return redirect("/parents")

@app.route("/parents", methods=["GET", "POST"])
@count_required
def parents():
    # checks for method
    if request.method == "GET":
        return render_template("parents.html", count=session['count'])
    else:
        # check notes
        session['parents'] = [{}]
        for i in range(session['count']):
            # checks which traits are homo dom, homo rec, or hetero for parents
            if not len(session['parents'][0]):
                session['parents'][0]['p1'] = request.form.get('p1t0')
                session['parents'][0]['p2'] = request.form.get('p2t0')
            else:
                session['parents'].append({'p1': request.form.get(f'p1t{i}')})
                session['parents'][i]['p2'] = request.form.get(f'p2t{i}')

        return redirect('/path')

@app.route("/path", methods=["GET", "POST"])
@count_required
def path():
    # checks if request method is post or get
    if request.method == "GET":
        return render_template("path.html")
    else:
        return redirect(request.form.get("route"))

@app.route("/calculate", methods=["GET", "POST"])
@count_required
def calc():
    # checks if request method is post or get
    if request.method == "GET":
        data = []
        counter = 0
        # get chance of genotypes
        for genotype in session['traits']:
            data.append(chance(session['parents'][counter]['p1'], session['parents'][counter]['p2'], genotype['dom_s'], genotype['rec_s']))
            counter += 1
        # checks for how many genes are input, chooses output based on that.
        if len(data) == 1:
            return render_template("calc.html", data=data)
        else:
            return render_template("calc2.html", data=mult(data))

    else:
        return error("Unimplemented", 501)

@app.route("/specify", methods=["GET", "POST"])
@count_required
def specify():
    if request.method == 'GET':
        doms = []
        recs = []
        for trait in session['traits'][0]['dom_n']:
            doms.append(trait)
        for trait in session['traits'][0]['rec_n']:
            recs.append(trait)
        names = sorted(doms + recs)
        return render_template("specify.html", traits=map(json.dumps, names))
    else:
        return error("Unimplemented", 501)

# Handle InternalServerError (unexpected error) [from application.py in Finance]
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error("Internal Server Error", 500)

# Listen for errors [from application.py in Finance]
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)