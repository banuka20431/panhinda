from typing import List

from flask import request, render_template, session
from flask_login import current_user  # type: ignore

from app import app, db
from sqlalchemy import select

from app.articles.models import Article
from app.utils.validator import *
from app.utils.errors import *

from app.extensions import logger


# Handle custom BaseError exceptions and render a generic error page
@app.errorhandler(BaseError)
def render_error_page(e: str):
    return render_template("error.html", error=str(e)), 500


# Handle 401 Unauthorized errors
@app.errorhandler(401)
def render_error_page_401(e: str):
    return render_template("error.html", error=NotAuthorizedError()), 401


# Handle 403 Forbidden errors
@app.errorhandler(403)
def render_error_page_403(e: str):
    return render_template("error.html", error=ForbiddenError()), 403


# Handle 404 Not Found errors
@app.errorhandler(404)
def render_error_page_404(e: str):
    return render_template("error.html", error=ContentNotFoundError()), 404


# Handle 405 Method Not Allowed errors
@app.errorhandler(405)
def render_error_page_405(e: str):
    return render_template("error.html", error=MethodNotAllowedError()), 405


# Handle 500 Internal Server Error
@app.errorhandler(500)
def render_error_page_500(e: str):
    return render_template("error.html", error=InternalServerError()), 500


@app.before_request
def get_profile_stat() -> None:

    if request.endpoint in ['static', 'render_error_page_404', 'render_error_page_500']:
        return

    session["articles_wrote_count"] = 0
    session["likes_gained"] = 0

    if current_user.is_authenticated:  # type: ignore

        articles_wrote: List[Article] = db.session.scalars(
            select(Article).where(Article.author_id == current_user.id)  # type: ignore
        ).all() or []

        session["articles_wrote_count"] = len(articles_wrote)

        session["likes_gained"] = sum(
            [len(article.likes) for article in articles_wrote]
        )


# Route for the home page
@app.route("/", methods=["GET"])
def index() -> str:
    if request.method == "GET":

        articles_wrote_count = 0
        likes_gained = 0

        try:

            if current_user.is_authenticated:  # type: ignore
                
                articles_wrote = db.session.scalars(
                    select(Article).where(Article.author_id == current_user.id)  # type: ignore
                ).all()

                articles_wrote = articles_wrote or []
                
                articles_wrote_count = len(articles_wrote)
                
                likes_gained = [len(article.comments) for article in articles_wrote]

            return render_template(
                "index.html",
                articles_wrote_count=articles_wrote_count,
                likes_gained=likes_gained,
            )

        except AttributeError as e:
            logger.error(f"app/routes: Attribute Error {e}")
            return render_template("error.html", error=InternalServerError())

    else:
        return "Method not allowed"
