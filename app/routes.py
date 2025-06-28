from flask import request, render_template, flash, redirect, url_for
from app import app
from app.utils.validator import *
from app.utils.errors import *

# Handle custom BaseError exceptions and render a generic error page
@app.errorhandler(BaseError)
def render_error_page(e):
    return render_template('error.html', error=e)

# Handle 401 Unauthorized errors
@app.errorhandler(401)
def render_error_page_401(e):
    return render_template('error.html', error=NotAuthorizedError())

# Handle 403 Forbidden errors
@app.errorhandler(403)
def render_error_page_403(e):
    return render_template('error.html', error=ForbiddenError())

# Handle 404 Not Found errors
@app.errorhandler(404)
def render_error_page_404(e):
    return render_template('error.html', error=ContentNotFoundError())

# Handle 405 Method Not Allowed errors
@app.errorhandler(405)
def render_error_page_405(e):
    return render_template('error.html', error=MethodNotAllowedError())

# Handle 500 Internal Server Error and print the error for debugging
@app.errorhandler(500)
def render_error_page_500(e):
    return render_template('error.html', error=InternalServerError())

# Route for the home page
@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        # This branch is redundant since only GET is allowed, but included for completeness
        return "Method not allowed"
