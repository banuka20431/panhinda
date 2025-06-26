from app import app, db
from app.articles.models import Article, Comment, Like, Category, SubCategory
from flask import request, render_template, redirect, url_for, flash, abort
from app.articles import bp

from sqlalchemy import select, delete, update
from flask_login import current_user, login_required
from datetime import datetime, timezone

from app.utils.errors import ContentNotFoundError

from app.utils.validator.article_forms import CreateArticleForm
from app.utils.func import flash_errors


@bp.route("/", methods=["GET"])
def view_articles():
    if request.method == "GET":

        articles = db.session.scalars(select(Article)).all()

        return render_template("articles/index.html", articles=articles)


@bp.route("/<int:article_id>", methods=["GET"])
def view_article(article_id: int):

    if request.method == "GET":
        
        article = db.session.get(Article, article_id)
        
        if article is None : 
            abort(404)

        comment_to_edit = None

        if request.args.get("comment_id_to_edit", False):
            
            comment_to_edit = db.session.get(
                Comment, int(request.args.get("comment_id_to_edit"))
            )

        return render_template(
            "articles/read.html", article=article, comment_to_edit=comment_to_edit
        )


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
            category_id=db.session.scalar(select(SubCategory.category_id).where(SubCategory.label==form.category.data))
        )
        
        db.session.add(new_article)

        db.session.commit()

        return redirect(url_for('articles.view_article', article_id=new_article.id))

    else :
        flash_errors(form)

    return redirect(url_for('auth.create'))
        


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
            flash("Comment must not exceed 1000 characters", category='error')

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

                    db.session.execute(
                        update(Comment)
                        .where(Comment.id == int(comment_id))
                        .values(body=body, edited=datetime.now(timezone.utc))
                    )
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
                flash("Comment must not exceed 1000 characters", category='error')

            else:
        
                db.session.execute(
                    update(Comment).where(Comment.id==comment.id).values(body=body, edited=datetime.now(timezone.utc))
                )
        
                db.session.commit()
            
            return redirect(url_for("articles.view_article", article_id=article_id))

@bp.route('<int:id>/search', methods=['GET'])
def search(article_id=None):
    query = request.args.get('q')
    print(query)
    return redirect(url_for('articles.view_articles'))

@bp.route('/search', methods=['GET'])
def global_search():
    query = request.args.get('q')
    print(query)
    return redirect(url_for('articles.view_articles'))