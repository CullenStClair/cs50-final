from flask import render_template

def error(message="Bad request", code=400):
    return render_template("error.html", code=code, message=message), code