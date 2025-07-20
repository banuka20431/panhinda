from flask import request, render_template, url_for, redirect, flash, request
from flask_login import login_required
from sqlalchemy import select, update
from flask_login import current_user
import requests

from app import app, db
from app.articles.models import Article, Like, Category
from app.auth.models import UserInterest, User
from app.profile import bp
from app.utils.validator.profile_forms import PersonalInformationForm, AddInterestsForm
from app.utils.func import flash_errors


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

    if form.validate_on_submit():

        changes = 0

        if form.first_name.data != current_user.first_name:
            current_user.first_name=form.first_name.data
            changes += 1
        
        if form.last_name.data != current_user.last_name:
            current_user.last_name=form.last_name.data
            changes += 1
        
        if form.first_name.data != current_user.first_name:
            current_user.username=form.username.data
            changes += 1

        if not changes:
            flash('No updates were made', category='error')        
        else:
            db.session.commit()
            flash('Data updated successfully')
    
    else:

        flash_errors(form)

    return redirect(url_for('profile.view_profile_personal_info'))
            


@bp.route("/my-articles", methods=["GET", "POST"])
@login_required
def view_profile_my_articles():
    if request.method == "GET":
        
        articles = db.session.scalars(
                select(Article).where(Article.author_id == current_user.id)
        ).all()

        print(articles[0].title)
        
        return render_template("profile/index.html", sub_route="my_articles", articles=articles)


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
            category_count=len(Category.query.all())
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

        liked_articles = [
            like.article
            for like in db.session.scalars(
                select(Like).where(Like.user_id == current_user.id)
            ).all()
        ]


        return render_template(
            "profile/index.html",
            sub_route="liked_articles",
            liked_articles=liked_articles,
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

def upload_image_to_catbox(image_path):
    files = {'fileToUpload': image_path}
    response = requests.post('https://catbox.moe/user/api.php', files=files, data={'reqtype': 'fileupload'})

    return response.text

@bp.route("/update-profile-picture", methods=["POST"])
@login_required
def update_profile_picture():
    file = None 
    # check if the request contains a image file
    if 'pro_pic' in request.files:
        file = request.files['pro_pic']
    
    # upload the file to cloud if it exists
    if file is not None:
        dpUrl = upload_image_to_catbox(file)

        current_user.profile_picture_uri = dpUrl
        
        db.session.commit()

        flash("Profile Picture Updated!", category='success')

    else:
        
        flash("Please select a image", category='error')
    
    return redirect(url_for('profile.view_profile'))
    