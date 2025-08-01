from app import app, db
from app.articles.models import Article, Comment, Like, Category, SubCategory
from flask import request, render_template, redirect, url_for, flash, abort
from app.articles import bp

from sqlalchemy import select, delete, update, and_
from flask_login import current_user, login_required
from datetime import datetime, timezone

from app.utils.errors import ContentNotFoundError

from app.utils.validator.article_forms import CreateArticleForm
from app.utils.func import flash_errors
from app.utils.sort_engine import Search

from random import randint


@bp.route("/", methods=["GET"])
def view_articles(filtered: tuple[int] | None = None):
    if request.method == "GET":

        articles_ = db.session.scalars(select(Article)).all()

        if current_user.is_authenticated:
            articles = [article for article in articles_ if article.author.id != current_user.id]
        
        else:

            articles = articles_

        if filtered is None:

            return render_template("articles/index.html", articles=articles)
        
        flash(f'{len(filtered)} {'article found' if len(filtered) == 1 else 'articles found' }', category='info')
        
        return render_template(
            "articles/index.html", articles=[a for a in articles_ if a.id in filtered]
        )


@bp.route("/<int:article_id>", methods=["GET"])
def view_article(article_id: int, search_matches: list[tuple[int, int]] | None = None):

    if request.method == "GET":

        liked_before = False

        if current_user.is_authenticated:

            liked_before = db.session.scalar(select(Like).where(and_(Like.user_id==current_user.id, Like.article_id==article_id)))

        article = db.session.get(Article, article_id)

        if article is None:
            abort(404)

        comment_to_edit = None

        if request.args.get("comment_id_to_edit", False):

            comment_to_edit = db.session.get(
                Comment, int(request.args.get("comment_id_to_edit"))
            )

        if search_matches is not None:
            body = article.body
            highlighted_body = ""
            last_idx = 0
            for start, end in search_matches:
                highlighted_body += body[last_idx:start]
                highlighted_body += "<span style='background-color: rgba(0,255,222,.5);'>" + body[start:end] + "</span>"
                last_idx = end
            highlighted_body += body[last_idx:]
            article.body = highlighted_body

            flash(f'{len(search_matches)} {'match found' if len(search_matches) == 1 else 'matches found' }', category='info')
            

        return render_template(
            "articles/read.html", article=article, comment_to_edit=comment_to_edit, liked_before=liked_before
        )
    
@bp.route("/rand", methods=["GET"])
def view_suggested_article():
    if request.method == 'GET':
        suggested_id = randint(1, db.session.scalars(select(Article)).all()[-1].id)
        return redirect(url_for('articles.view_article', article_id=suggested_id))


@bp.route("/create", methods=["GET", "POST"])
@login_required
def view_create_article():
    form = CreateArticleForm()
    if request.method == "GET":
        return render_template("articles/create.html", form=form)

    if form.validate_on_submit():

        new_article = Article(
            author_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            body=form.body.data,
            category_id=db.session.scalar(
                select(SubCategory.category_id).where(
                    SubCategory.label == form.category.data
                )
            ),
        )

        db.session.add(new_article)

        db.session.commit()

        return redirect(url_for("articles.view_article", article_id=new_article.id))

    else:
        flash_errors(form)

    return redirect(url_for("articles.view_create_article"))


@bp.route("/delete/<int:article_id>", methods=["GET", "POST"])
@login_required
def view_delete_article(article_id):
    db.session.execute(delete(Article).where(Article.id==article_id))
    db.session.commit()
    return redirect(url_for('profile.view_profile_my_articles'))


@bp.route("/edit/<int:article_id>", methods=["GET", "POST"])
@login_required
def view_edit_article(article_id):
    
    if request.method == 'GET':
        db.session.execute(delete(Article).where(id=article_id))
    
    return redirect(url_for('profile.view_profile_my_articles'))


@bp.route("/<int:article_id>/react", methods=["POST"])
@login_required
def react(article_id):

    def __add_like():
        new_like = Like(article_id=article_id, user_id=current_user.id)
        db.session.add(new_like)
        db.session.commit()

    def __remove_like():
        db.session.execute(delete(Like).where(Like.user_id == int(current_user.id)))
        db.session.commit()

    if request.method == "POST":

        article_id = request.form.get("article_id")
        likes = db.session.get(Article, int(article_id)).likes

        if current_user.id != db.session.get(Article, int(article_id)).author.id:

            if not likes:
                __add_like()
            else:
                for like in likes:
                    if int(current_user.id) == like.user.id:
                        __remove_like()
                        break
                else:
                    __add_like()

        return redirect(url_for("articles.view_article", article_id=article_id))


@bp.route("/<int:article_id>/comment", methods=["POST"])
@login_required
def comment(article_id=None):

    if request.method == "POST":

        body = request.form.get("body")

        if not body:
            return redirect(url_for("articles.view_article", article_id=article_id))

        if len(body) > 1000:
            flash("Comment must not exceed 1000 characters", category="error")

        else:

            if request.form.get("comment") == "Post Comment":
                new_comment = Comment(
                    body=body, article_id=article_id, user_id=current_user.id
                )
                db.session.add(new_comment)
                db.session.commit()

            if request.form.get("comment") == "Update":

                comment_id = request.form.get("comment_id")
                comment = db.session.get(Comment, int(comment_id))

                if comment.user.id == int(current_user.id) and comment.body != body:

                    comment.body = body 
                    comment.edited = datetime.now(timezone.utc)

                    db.session.commit()

        return redirect(url_for("articles.view_article", article_id=article_id))


@bp.route("/<int:article_id>/delete_comment", methods=["POST"])
@login_required
def delete_comment(article_id: int):
    if request.method == "POST":

        comment_id = request.form.get("comment_id")

        comment = db.session.get(Comment, int(comment_id))

        if comment.user.id == current_user.id:
            db.session.execute(delete(Comment).where(Comment.id == int(comment_id)))
            db.session.commit()

    return redirect(url_for("articles.view_article", article_id=article_id))


@bp.route("/<int:article_id>/edit_comment", methods=["GET", "POST"])
@login_required
def edit_comment(article_id: int):

    if request.method == "GET":

        comment_id = request.args.get("comment_id")
        article_id = request.args.get("article_id")
        return redirect(
            url_for(
                "articles.view_article",
                article_id=article_id,
                comment_id_to_edit=int(comment_id),
            )
        )

    if request.method == "POST":

        comment_id = request.form.get("comment_id")
        comment = db.session.get(Comment, int(comment_id))

        if comment.user.id == current_user.id:

            body = request.form.get("body")

            if len(body) > 1000:
                flash("Comment must not exceed 1000 characters", category="error")

            else:

                comment.body = body
                comment.edited = datetime.now(timezone.utc)

                db.session.commit()

            return redirect(url_for("articles.view_article", article_id=article_id))


@bp.route("/<int:article_id>/search", methods=["GET"])
def local_search(article_id):
    query = request.args.get("q")
    new_search = Search(query, article_id)
    return view_article(article_id, search_matches=new_search.get_matches())


@bp.route("/search", methods=["GET"])
def global_search():
    query = request.args.get("q")
    new_search = Search(query)
    a = new_search.get_results()
    return view_articles(filtered=new_search.get_results())
