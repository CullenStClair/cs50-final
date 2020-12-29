# Copyright Cullen St. Clair and Kamran Yaghoubian 2020

from tempfile import mkdtemp

from flask import Flask, redirect, render_template, request, session, make_response, jsonify
from flask_session import Session
from werkzeug.exceptions import (HTTPException, InternalServerError, default_exceptions)
from ast import literal_eval

from random import randint

from helpers import *

# Configure Flask application
app = Flask(__name__)

# Ensure templates are auto-reloaded [from application.py in Finance]
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached [from application.py in Finance]
@app.after_request
def after_request(response):
    if request.endpoint != 'giveprob':
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
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
        # create temporary user_id (random 10-digit int)
        session['user_id'] = randint(1000000000, 9999999999)
        # checks for number of at least 2
        if count < 2:
            return error("Forbidden: Invalid number of genes. Minimum of 2.", 403)

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
        for trait in session['traits']:
            for trait2 in session['traits']:
                if trait['dom_n'] == trait2['dom_n']:
                    return error("No repeating traits", 403)
                elif trait['dom_s'] == trait2['dom_s']:
                    return error("No repeating symbols", 403)
                elif trait['rec_n'] == trait2['rec_n']:
                    return error("No repeating traits", 403)
                elif trait['rec_s'] == trait2['rec_s']:
                    return error("No repeating symbols", 403)
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
            return render_template("calc.html", data=data, function=which_traits, traits=session['traits'])
        else:
            return render_template("calc2.html", data=mult(data), function=which_traits, traits=session['traits'])
    else:
        return error("Unimplemented", 501)


@app.route("/specify", methods=["GET", "POST"])
@count_required
def specify():
    if request.method == 'GET':
        # initial data format
        names = []
        for i in range(session['count']):
            names.append(session['traits'][i]['dom_n'])
            names.append(session['traits'][i]['rec_n'])
        names = sorted(names)
        safenames = ','.join(names)
        sessiondat = [session['traits'], session['parents']]
        return render_template("specify.html", genes=safenames, session=sessiondat)
    else:
        return error("Unimplemented", 501)


@app.route("/specify/prob")
def giveprob():
    """Server route which returns a JSON with the probability of (args) traits showing together."""
    args = request.args.to_dict(False)
    traitnames = list(args['traits'][0].split(","))
    sessiondat = literal_eval(args['session'][0])
    traits = sessiondat[0]
    parentsdat = sessiondat[1]
    result = prob(traitnames, traits, parentsdat)
    return jsonify({"data": f"{result}"})


def errorhandler(e):
    """Handle InternalServerError (unexpected error) [from application.py in Finance]."""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return error("Internal Server Error", 500)


# Listen for errors [from application.py in Finance]
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
