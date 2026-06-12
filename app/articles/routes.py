from typing import cast

from app import db
from app.articles.models import Article, Comment, Like, SubCategory
from flask import request, render_template, redirect, url_for, flash, abort
from app.articles import bp

from sqlalchemy import select, delete, and_
from flask_login import current_user, login_required  # type: ignore
from datetime import datetime, timezone


from app.articles.forms import CreateArticleForm
from app.utils.func import flash_errors
from app.utils.sort_engine import Search

from random import randint


@bp.route("/", methods=["GET"])  # type: ignore
def view_articles(filtered: tuple[int] | None = None):
    if request.method == "GET":

        articles_ = db.session.scalars(select(Article)).all()

        if current_user.is_authenticated:  # type: ignore
            articles = [
                article for article in articles_ if article.author.id != current_user.id  # type: ignore
            ]

        else:

            articles = articles_

        if filtered is None:

            return render_template("articles/index.html", articles=articles)

        flash(
            f"{len(filtered)} {'article found' if len(filtered) == 1 else 'articles found' }",
            category="info",
        )

        return render_template(
            "articles/index.html", articles=[a for a in articles_ if a.id in filtered]
        )


@bp.route("/<int:article_id>", methods=["GET"])  # type: ignore
def view_article(article_id: int, search_matches: list[tuple[int, int]] | None = None):

    if request.method == "GET":

        liked_before = False

        if current_user.is_authenticated:  # type: ignore

            liked_before = db.session.scalar(
                select(Like).where(
                    and_(Like.user_id == current_user.id, Like.article_id == article_id)  # type: ignore
                )
            )

        article = db.session.get(Article, article_id)

        if article is None:
            abort(404)

        comment_to_edit = None

        if request.args.get("comment_id_to_edit", False):

            comment_to_edit = db.session.get(
                Comment, cast(int, request.args.get("comment_id_to_edit"))
            )

        if search_matches is not None:
            body = article.body
            highlighted_body = ""
            last_idx = 0
            for start, end in search_matches:
                highlighted_body += body[last_idx:start]
                highlighted_body += (
                    "<span style='background-color: rgba(0,255,222,.5);'>"
                    + body[start:end]
                    + "</span>"
                )
                last_idx = end
            highlighted_body += body[last_idx:]
            article.body = highlighted_body

            flash(
                f"{len(search_matches)} {'match found' if len(search_matches) == 1 else 'matches found' }",
                category="info",
            )

        return render_template(
            "articles/read.html",
            article=article,
            comment_to_edit=comment_to_edit,
            liked_before=liked_before,
        )


@bp.route("/rand", methods=["GET"])  # type: ignore
def view_suggested_article():
    if request.method == "GET":
        articals = db.session.scalars(select(Article)).all()
        suggested_id = (
            randint(1, articals[len(articals) - 1].id) if len(articals) > 0 else -1
        )

        if suggested_id == -1:
            return redirect(url_for("articles.view_articles"))

        return redirect(url_for("articles.view_article", article_id=suggested_id))


@bp.route("/create", methods=["GET", "POST"])
@login_required
def view_create_article():
    form = CreateArticleForm()
    if request.method == "GET":
        return render_template("articles/create.html", form=form)

    if form.validate_on_submit():  # type: ignore

        __category_id = db.session.scalar(
            select(SubCategory.category_id).where(
                SubCategory.label == form.category.data
            )
        )

        new_article = (
            Article(
                author_id=current_user.id,  # type: ignore
                title=str(form.title.data),
                description=str(form.description.data),
                body=str(form.body.data),
                category_id=cast(int, __category_id),
            ),
        )

        db.session.add(new_article)

        db.session.commit()

        return redirect(url_for("articles.view_article", article_id=new_article.id)) # type: ignore

    else:
        flash_errors(form)

    return redirect(url_for("articles.view_create_article"))


@bp.route("/delete/<int:article_id>", methods=["GET", "POST"])
@login_required
def view_delete_article(article_id: int):
    db.session.execute(delete(Article).where(Article.id == article_id))
    db.session.commit()
    return redirect(url_for("profile.view_profile_my_articles"))


@bp.route("/edit/<int:article_id>", methods=["GET", "POST"])
@login_required
def view_edit_article(article_id: int):

    if request.method == "GET":
        db.session.execute(delete(Article).where(id=article_id))  # type: ignore

    return redirect(url_for("profile.view_profile_my_articles"))


@bp.route("/<int:article_id>/react", methods=["POST"])  # type: ignore
@login_required
def react(article_id: int):

    def __add_like():
        new_like = Like(article_id=article_id, user_id=current_user.id)  # type: ignore
        db.session.add(new_like)
        db.session.commit()

    def __remove_like():
        db.session.execute(delete(Like).where(Like.user_id == int(current_user.id)))  # type: ignore
        db.session.commit()

    if request.method == "POST":

        article_id = cast(int, request.form.get("article_id"))
        res = db.session.get(Article, int(article_id))
        likes = res.likes if res else 0

        res = db.session.get(Article, int(article_id))

        if res and (current_user.id != res.author.id):  # type: ignore

            if not likes:
                __add_like()
            else:
                for like in likes:
                    if int(current_user.id) == like.user.id:  # type: ignore
                        __remove_like()
                        break
                else:
                    __add_like()

        return redirect(url_for("articles.view_article", article_id=article_id))


@bp.route("/<int:article_id>/comment", methods=["POST"])  # type: ignore
@login_required
def comment(article_id: int | None = None):

    if request.method == "POST":

        body = request.form.get("body")

        if not body:
            return redirect(url_for("articles.view_article", article_id=article_id))

        if len(body) > 1000:
            flash("Comment must not exceed 1000 characters", category="error")

        else:

            if request.form.get("comment") == "Post Comment" and article_id != None:
                new_comment = Comment(
                    body=body, article_id=article_id, user_id=current_user.id  # type: ignore
                )
                db.session.add(new_comment)
                db.session.commit()

            if request.form.get("comment") == "Update":

                comment_id = cast(int, request.form.get("comment_id"))
                comment: Comment | None = db.session.get(Comment, comment_id)

                if comment and comment.user.id == int(current_user.id) and comment.body != body:  # type: ignore

                    comment.body = body
                    comment.edited = datetime.now(timezone.utc)

                    db.session.commit()

        return redirect(url_for("articles.view_article", article_id=article_id))


@bp.route("/<int:article_id>/delete_comment", methods=["POST"])
@login_required
def delete_comment(article_id: int):
    if request.method == "POST":

        comment_id: int = cast(int, request.form.get("comment_id"))

        comment: Comment | None = db.session.get(Comment, comment_id)

        if comment and comment.user.id == current_user.id:  # type: ignore
            db.session.execute(delete(Comment).where(Comment.id == int(comment_id)))
            db.session.commit()

    return redirect(url_for("articles.view_article", article_id=article_id))


@bp.route("/<int:article_id>/edit_comment", methods=["GET", "POST"])  # type: ignore
@login_required
def edit_comment(article_id: int):

    if request.method == "GET":

        comment_id = cast(int, request.args.get("comment_id"))
        article_id = cast(int, request.args.get("article_id"))

        return redirect(
            url_for(
                "articles.view_article",
                article_id=article_id,
                comment_id_to_edit=int(comment_id),
            )
        )

    if request.method == "POST":

        comment_id = cast(int, request.form.get("comment_id"))
        comment: Comment | None = db.session.get(Comment, int(comment_id))

        if comment and comment.user.id == current_user.id:  # type: ignore

            body = str(request.form.get("body"))

            if len(body) > 1000:
                flash("Comment must not exceed 1000 characters", category="error")

            else:

                comment.body = body
                comment.edited = datetime.now(timezone.utc)

                db.session.commit()

            return redirect(url_for("articles.view_article", article_id=article_id))


@bp.route("/<int:article_id>/search", methods=["GET"])  # type: ignore
def local_search(article_id: int):

    query = str(request.args.get("q"))
    new_search = Search(query, article_id)
    return view_article(article_id, search_matches=new_search.get_matches())


@bp.route("/search", methods=["GET"])  # type: ignore
def global_search():

    query = str(request.args.get("q"))
    new_search = Search(query)
    return view_articles(filtered=new_search.get_results())
