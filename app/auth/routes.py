from app import app, db, mail
from flask import request, render_template, redirect, flash, url_for, session, abort
from flask_login import current_user, login_user
from app.auth.models import User
from app.auth import bp

from sqlalchemy import select
from flask_login import logout_user
from urllib.parse import urlsplit
from flask_mail import Message
from datetime import datetime, timezone
from itsdangerous import URLSafeTimedSerializer as Serializer

from app.utils.validator import (
    LoginForm,
    LoginVerificationForm,
    RegisterationUserDetailsForm,
    ResetPasswordForm,
    RegistretionUserCredentialsForm,
)
from app.utils.func import get_sha256_hash, flash_errors, remove_url_suffix, session_get_or_404
from app.utils.errors import InternalServerError


def send_email_confirmation(user: User):

    token = user.get_email_verification_token()

    SUBJECT = "Sending confirmation link"

    mail_conf_mail = Message(
        SUBJECT, sender=app.config.get("MAIL_USERNAME"), recipients=[user.email]
    )

    mail_conf_mail.html = render_template(
        "auth/emails/conf_email.html",
        user_name=user.first_name,
        link=url_for("auth.verify_email", token=token, _external=True),
        current_year=datetime.now(timezone.utc).year,
    )

    print(f'\n\n Sent : {token}\n\n')

    try:
        mail.send(mail_conf_mail)
    except:
        return False
    
    return True

@bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()

    if request.method == "GET":

        return render_template("auth/login/index.html", form=form)

    if form.validate_on_submit():

        session['remember_me'] = form.remember_me.data
        session['next'] = request.args.get('next')

        user: User = db.session.scalar(
            select(User).where(User.username == form.username.data)
        )

        if not user.check_password(form.password.data):
            flash("User Couldn't be Authorized", category='error')
            session["attampted_user"] = form.username.data
            flash_errors(form)
            return redirect(url_for("auth.login"))
        
        session['login_user'] = user
        return redirect(url_for('auth.login_user_verification'))
    
    else:
        flash_errors(form)
        return redirect(url_for("auth.login"))
    
@bp.route('/user-verification', methods=['GET', 'POST'])
def login_user_verification():
    
    form = LoginVerificationForm()
    user: User = session_get_or_404('login_user')
    
    if request.method == 'GET':

        if not session.get('auth_attempts', False):
            user.send_otp()
        
        if session.get('auth_attempts', 0) == 3:
            
            session.pop('auth_attempts')
            flash('Authentication Failed', category='error')
            session.pop('login_user')
        
            return redirect(url_for('auth.login'))
        

        session['auth_attempts'] = session.get('auth_attempts', 0) + 1
        
        return render_template('auth/login/user_verification.html', form=form)
    
    if not form.validate_on_submit():
        if session_get_or_404('auth_attempts') != 3 :
            flash(f'You have   {3 - session['auth_attempts']  } tries left', category='error')
        flash_errors(form)
        return redirect(url_for('auth.login_user_verification'))

    state, flag = user.verify_otp(form.otp.data) 

    if not state:

        match flag:
            case User.TIME_OUT:
                flash("Authentication Failed! OTP Expired", category='error')
                return redirect('auth.login')
            case User.NOT_MATCHED:
                flash("OTP Incorrect!", category='error')

        if session_get_or_404('auth_attempts') != 3 :
            flash(f'You have   {3 - session['auth_attempts']  } tries left', category='error')
        return redirect(url_for('auth.login_user_verification'))
        
    else:
        session.pop('auth_attempts')
        session.pop('login_user')
        login_user(user, remember=session.pop('remember_me'))
        
        next_page = session.pop('next')

        if next_page == "None":
            return redirect(url_for("index"))
        else:

            next_page = remove_url_suffix(next_page, ["/react", "/comment"])
            print("?next=" + next_page)

            if not next_page or urlsplit(next_page).netloc != "":
                next_page = url_for("index")

            return redirect(next_page)
   

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    form = ResetPasswordForm()

    if request.method == "GET":
        return render_template("auth/password_reset.html", form=form)

    if request.method == "POST":

        attampted_login_username = session.pop("attampted_user", None)

        if attampted_login_username is None:
            raise InternalServerError(previous_url=url_for("auth.login"))

        if form.validate_on_submit():



            flash("Password Reset Successfull", category="info")
            return redirect(url_for("auth.login"))

        else:
            flash_errors(form)
            return redirect(url_for("auth.reset_password"))


@bp.route("/register/user-details", methods=["GET", "POST"])
def register_user_details():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegisterationUserDetailsForm()

    if request.method == "GET":
        return render_template("auth/register/user-details.html", form=form)

    if form.validate_on_submit():

        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            dob=form.dob.data,
            gender="M" if form.gender.data == "Male" else "F",
            email=form.email.data,
            phone_number=get_sha256_hash(form.phone_number.data),
            phone_number_last_digits=form.phone_number.data[-1:-4],
        )
        session["new_user"] = new_user

        return redirect(url_for("auth.register_user_credentials"))

    else:

        flash_errors(form)

        return redirect(url_for("auth.register_user_details"))


@bp.route("/register/user-credentials", methods=["GET", "POST"])
def register_user_credentials():

    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = RegistretionUserCredentialsForm()

    if request.method == "GET":
        return render_template("auth/register/user-credentials.html", form=form)

    if form.validate_on_submit():

        new_user: User = session_get_or_404("new_user")

        if new_user:

            new_user.username = form.username.data
            new_user.set_password(form.password.data)
            
            if send_email_confirmation(new_user):
                flash("Email Confirmation link sent Successfully. Please check your emails!", category='success')
            else:
                flash("Email Verification Failed!", category='error')
            
            try:
                db.session.add(new_user)
                db.session.flush() # flush to assign id to the user without commiting
                db.session.commit()
            except:
                flash("Failed to Create the Account!")
                abort(500)
            else:
                flash("Account Created Successfully", category='success')
            
            return redirect(url_for('auth.login'))

        else:
            raise InternalServerError(
                previous_url=url_for("auth.register_user_details")
            )

    else:

        flash_errors(form)

        return redirect(url_for("auth.register_user_credentials"))
    

@bp.route("verify-email/<string:token>")
def verify_email(token):

    confirmed = False

    if token:

        print(f'\n\n verify : {token}\n\n')

        if email := User.verify_email_token(token):
            user = db.session.scalar(select(User).where(User.email==email))
            user.verified = True
            user.email == get_sha256_hash(email)
            db.session.commit()

            confirmed = True

    return render_template("auth/emails/sent_email_state.html", confirmed=confirmed)
