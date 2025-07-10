from flask import request, render_template, flash, redirect, url_for, session
from flask_login import current_user

from app import app, db
from sqlalchemy import select, func

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

# Handle 500 Internal Server Error 
@app.errorhandler(500)
def render_error_page_500(e):
    return render_template('error.html', error=InternalServerError())

@app.before_request
def get_profile_stat():
    
    session['articles_wrote_count'] = 0
    session['likes_gained'] = 0

    if current_user.is_authenticated:
        articles_wrote = db.session.scalars(select(Article).where(Article.author_id==current_user.id)).all()
        session['articles_wrote_count'] = len(articles_wrote)
        for article in articles_wrote:
            session['likes_gained'] += len(article.comments)
            

# Route for the home page
@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":

        articles_wrote_count = 0
        likes_gained = 0

        if current_user.is_authenticated:
            articles_wrote = db.session.scalars(select(Article).where(Article.author_id==current_user.id)).all()
            articles_wrote_count = len(articles_wrote)
            for article in articles_wrote:
                likes_gained += len(article.comments)

        return render_template("index.html", articles_wrote_count=articles_wrote_count, likes_gained=likes_gained)
    else:
        # This branch is redundant since only GET is allowed, but included for completeness
        return "Method not allowed"
