from flask import request, render_template, flash, redirect, url_for
from app import app
from app.utils.validator import *
from app.utils.errors import *

@app.errorhandler(BaseError)
def render_error_page(e):
    return render_template('error.html', error=e)

@app.errorhandler(401)
def render_error_page_401(e):
    return render_template('error.html', error=NotAuthorizedError())

@app.errorhandler(403)
def render_error_page_403(e):
    return render_template('error.html', error=ForbiddenError())

@app.errorhandler(404)
def render_error_page_404(e):
    return render_template('error.html', error=ContentNotFoundError())

@app.errorhandler(405)
def render_error_page_405(e):
    return render_template('error.html', error=MethodNotAllowedError())

@app.errorhandler(500)
def render_error_page_500(e):
    print(e)
    return render_template('error.html', error=InternalServerError())

@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        return "Method not allowed"
