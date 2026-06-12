from typing import cast

from flask import request, render_template, url_for, redirect, flash
from flask_login import login_required, current_user  # type: ignore
from sqlalchemy import select

from app import db
from app.articles.models import Article, Like, Category
from app.auth.models import UserInterest, User
from app.profile import bp
from app.profile.forms import PersonalInformationForm, AddInterestsForm
from app.utils.func import flash_errors
from app.profile.services import upload_image_to_catbox

from app.auth.forms import LogonResetPasswordForm


@bp.route("/<int:author_id>", methods=["GET"])  # type: ignore
def view_author_profile(author_id: int):

    u = db.session.get(User, author_id)

    articles_wrote = len(u.articles)  # type: ignore
    likes_gained = sum([len(article.likes) for article in u.articles])  # type: ignore

    if request.method == "GET":
        return render_template(
            "profile/author_profile.html",
            author=u,
            articles_wrote=articles_wrote,
            likes_gained=likes_gained,
        )


@bp.route("/", methods=["GET"])  # type: ignore
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

    if form.validate_on_submit():  # type: ignore

        changes = 0

        if form.first_name.data != current_user.first_name:  # type: ignore
            current_user.first_name = form.first_name.data
            changes += 1

        if form.last_name.data != current_user.last_name:  # type: ignore
            current_user.last_name = form.last_name.data
            changes += 1

        if form.username.data != current_user.username:  # type: ignore
            current_user.username = form.username.data
            changes += 1

        if not changes:
            flash("No updates were made", category="error")
        else:
            db.session.commit()
            flash("Data updated successfully")

    else:

        flash_errors(form)

    return redirect(url_for("profile.view_profile_personal_info"))


@bp.route("/my-articles", methods=["GET", "POST"]) # type: ignore
@login_required
def view_profile_my_articles():
    if request.method == "GET":

        articles = db.session.scalars(
            select(Article).where(Article.author_id == current_user.id) # type: ignore
        ).all()

        return render_template(
            "profile/index.html", sub_route="my_articles", articles=articles
        )


@bp.route("/my-interests", methods=["GET", "POST"]) # type: ignore
@login_required
def view_profile_my_interests():

    form = AddInterestsForm()

    if request.method == "GET":

        interests = db.session.scalars(
            select(UserInterest).where(UserInterest.user_id == current_user.id) # type: ignore
        ).all()

        return render_template(
            "profile/index.html",
            sub_route="my_interests",
            interests=interests,
            form=form,
            category_count=len(Category.query.all()), # type: ignore
        )

    if form.validate_on_submit(): # type: ignore

        if form.interests.data:     
            for id in form.interests.data:
                new_iterest = UserInterest(int(id), int(current_user.id)) # type: ignore
                db.session.add(new_iterest)

        db.session.commit()

        return redirect(url_for("profile.view_profile_my_interests"))


@bp.route("/liked-articles", methods=["GET", "POST"]) # type: ignore
@login_required
def view_profile_liked_articles():
    if request.method == "GET":

        liked_articles = [
            like.article
            for like in db.session.scalars(
                select(Like).where(Like.user_id == current_user.id) # type: ignore
            ).all()
        ]

        return render_template(
            "profile/index.html",
            sub_route="liked_articles",
            liked_articles=liked_articles,
        )


@bp.route("/change-password", methods=["GET", "POST"])
@login_required
def view_profile_change_password():
    form = LogonResetPasswordForm()
    if request.method == "GET":
        return render_template(
            "profile/index.html", sub_route="change_password", form=form
        )

    if form.validate_on_submit(): # type: ignore
        current_user.set_password(form.password.data) # type: ignore
        flash("Password updated successfully")
        db.session.commit()
    else:
        flash_errors(form)

    return redirect(url_for("profile.view_profile_change_password"))


@bp.route("/delete-account", methods=["GET", "POST"]) # type: ignore
@login_required
def view_profile_delete_account():
    if request.method == "GET":
        return render_template("profile/index.html", sub_route="delete_account")


@bp.route("/update-profile-picture", methods=["POST"])
@login_required
def update_profile_picture():

    file = None

    if "pro_pic" in request.files:
        file = request.files["pro_pic"] # type: ignore

    # upload the file to cloud if it exists
    if file is not None:
        dpUrl = upload_image_to_catbox(cast(str, file))

        current_user.profile_picture_uri = dpUrl

        db.session.commit()

        flash("Profile Picture Updated!", category="success")

    else:

        flash("Please select a image", category="error")

    return redirect(url_for("profile.view_profile"))
