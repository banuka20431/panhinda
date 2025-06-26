from flask import request, render_template, url_for, redirect
from flask_login import login_required
from sqlalchemy import select
from flask_login import current_user

from app import app, db
from app.articles.models import Article, Like
from app.auth.models import UserInterest
from app.profile import bp
from app.utils.validator.profile_forms import PersonalInformationForm, AddInterestsForm


@bp.route("/", methods=["GET"])
@login_required
def view_profile():
    form = PersonalInformationForm()
    if request.method == "GET":
        return render_template(
            "profile/index.html", sub_route="personal_info", form=form
        )


@bp.route("/personal-info", methods=["GET", "POST"])
@login_required
def view_profile_personal_info():
    form = PersonalInformationForm()
    if request.method == "GET":
        return render_template(
            "profile/index.html", sub_route="personal_info", form=form
        )


@bp.route("/my-articles", methods=["GET", "POST"])
@login_required
def view_profile_my_articles():
    if request.method == "GET":
        with app.app_context():
            articles = db.session.scalars(
                select(Article).where(Article.author_id == current_user.id)
            ).all()
        return render_template(
            "profile/index.html", sub_route="my_articles", articles=articles
        )


@bp.route("/my-interests", methods=["GET", "POST"])
@login_required
def view_profile_my_interests():
    
    form = AddInterestsForm()
    
    if request.method == "GET":
        
        
        interests = db.session.scalars(select(UserInterest).where(UserInterest.user_id == current_user.id)).all()

        return render_template(
            "profile/index.html",
            sub_route="my_interests",
            interests=interests,
            form=form,
        )
    
    if form.validate_on_submit():
        
        for id in form.interests.data:
            new_iterest = UserInterest(int(id), int(current_user.id))
            db.session.add(new_iterest)
        
        db.session.commit()

        return redirect(url_for("profile.view_profile_my_interests"))


@bp.route("/liked-articles", methods=["GET", "POST"])
@login_required
def view_profile_liked_articles():
    if request.method == "GET":

        with app.app_context():
        
            liked_articles = [
                like.article
                for like in db.session.scalars(
                    select(Like).where(Like.user_id == current_user.id)
                ).all()
            ]

            authors = [
                liked_article.author.username for liked_article in liked_articles
            ]

        return render_template(
            "profile/index.html",
            sub_route="liked_articles",
            liked_articles=liked_articles,
            authors=authors,
        )


@bp.route("/authentication", methods=["GET", "POST"])
@login_required
def view_profile_authentication():
    if request.method == "GET":
        return render_template("profile/index.html", sub_route="authentication")


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def view_profile_change_password():
    if request.method == "GET":
        return render_template("profile/index.html", sub_route="change_password")


@bp.route("/delete-account", methods=["GET", "POST"])
@login_required
def view_profile_delete_account():
    if request.method == "GET":
        return render_template("profile/index.html", sub_route="delete_account")

@bp.route("/update-profile-picture", methods=["POST"])
@login_required
def update_profile_picture():
    return redirect(url_for('index'))