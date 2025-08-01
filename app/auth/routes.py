from app import app, db, mail
from flask import request, render_template, redirect, flash, url_for, session, abort
from flask_login import current_user, login_user
from app.auth.models import User
from app.auth import bp

from sqlalchemy import select, update
from flask_login import logout_user
from urllib.parse import urlsplit
from flask_mail import Message
from datetime import datetime, timezone, timedelta
from itsdangerous import URLSafeTimedSerializer as Serializer
from socket import gaierror

from app.utils.validator import (
    LoginForm,
    LoginVerificationForm,
    RegisterationUserDetailsForm,
    RegistretionUserCredentialsForm,
    EmailConfirmationResendForm,
    ResetPasswordForm,
    PasswordResetUserVerificationForm
    
)
from app.utils.func import get_sha256_hash, flash_errors, remove_url_suffix, session_get_or_404
from app.utils.errors import InternalServerError


def send_email_confirmation(user: User):

    token = user.get_email_verification_token()

    SUBJECT = "Sending confirmation link"

    mail_conf_mail = Message(
        SUBJECT, sender=app.config.get("MAIL_USERNAME"), recipients=[user.email]
    )

    user.email_conf_exp = datetime.now(timezone.utc) + timedelta(minutes=5)

    db.session.commit()    

    mail_conf_mail.html = render_template(
        "auth/emails/conf_email.html",
        user_name=user.first_name,
        link=f"https://clnhr9pt-5000.asse.devtunnels.ms/{url_for("auth.verify_email", token=token)}",
        current_year=datetime.now(timezone.utc).year,
    )

    try:
        mail.send(mail_conf_mail)
    except:
        return False
    
    return True

@bp.route("/resend-confirmation", methods=['GET', 'POST'])
def resend_email_confirmation():
    form = EmailConfirmationResendForm()

    if request.method == 'GET':
        
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        return render_template('auth/login/resend_email_confirmation.html', form=form)
    
    if form.validate_on_submit():
   
        if db.session.scalar(select(User.verified).where(User.username == form.username.data)):

            flash("That Email has already been verified")

        else:   
            id, email = db.session.execute(select(User.id, User.email).where(User.username == form.username.data)).first()
            
            if not form.email.data == email:
                flash("Sorry! Couldn't Verify the Email", category='error')
                return render_template('auth/login/resend_email_confirmation.html', form=form, **form.data)

            user = db.session.get(User, id)

            if timedelta(minutes=5) < (datetime.now(timezone.utc) - user.email_conf_exp.astimezone(timezone.utc)):
                send_email_confirmation(user)
                flash("Senḍ email confirmation successfully", category='info')
            else:
                flash("A confirmation email has already been sent to your address")

        return redirect(url_for('auth.login'))
    
    else:
        
        flash_errors(form)
        return redirect(url_for('auth.resend_email_confirmation'))

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
        
        email_verified = db.session.scalar(select(User.verified).where(User.username == form.username.data))

        if not email_verified:
            flash('Please verify your email before login', category='error')
            flash(f'<a href="{url_for('auth.resend_email_confirmation')}" class="underline underline-offset-2">Need to get the confimation again ?</a>', 'error')
            return redirect(url_for('auth.login'))
        
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
            try:
                user.send_otp()
            except (TimeoutError, gaierror):
                raise InternalServerError(previous_url=url_for('auth.login'))

         
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
                flash("Authentication Failed!  OTP Expired", category='error')
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
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return render_template("auth/login/password_reset.html", form=form)

    if form.validate_on_submit():

        attampted_login_username = session.pop("attampted_user", None)

        if attampted_login_username is None:
            raise InternalServerError(previous_url=url_for("auth.login"))
        
        else:
            u = db.session.scalar(select(User).where(User.username == attampted_login_username))

            if u.email != form.email.data:
                flash("User Couldn't be verified", category='error')
                flash("Password reset failed", category='error')
                return redirect(url_for('auth.login'))
            
            u.set_password(form.password.data)

            session['u'] = u

            u.send_otp()

            return redirect(url_for('auth.reset_password_user_verification'))

    else:
            
        flash_errors(form)

        return redirect(url_for("auth.reset_password"))
        
@bp.route("auth/reset-password-user-verification", methods=["GET", "POST"])
def reset_password_user_verification():

    form = PasswordResetUserVerificationForm()
    if request.method == 'GET':
        return render_template('auth/login/reset_password_user_verification.html', form=form)

    if form.validate_on_submit():

        user: User = session.pop("u", None)

        if user is None:
            raise InternalServerError(previous_url=url_for("auth.login"))
        
        if user.otp_hash == get_sha256_hash(form.otp.data):
            db.session.execute(update(User).values(password_hash=user.password_hash))
            db.session.commit()
            flash("Password reset successfully")
        else:
            flash("User couldn't be verified")
    
    return redirect(url_for('auth.login'))
    
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

        if email := User.verify_email_token(token):
            user = db.session.scalar(select(User).where(User.email==email))
            user.verified = True
            user.email == get_sha256_hash(email)
            db.session.commit()

            confirmed = True

    return render_template("auth/emails/sent_email_state.html", confirmed=confirmed)
