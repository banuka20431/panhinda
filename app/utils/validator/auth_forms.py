from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField
from wtforms import EmailField, BooleanField, SubmitField, DateField
from wtforms.validators import Length, EqualTo, DataRequired, InputRequired, Regexp
from wtforms.validators import email

from app.utils.validator.custom_validators import *


class UserVerificationForm(FlaskForm):
    pass


class LoginForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(max=32), CheckUsername()]
    )
    password = PasswordField("Password", validators=[InputRequired(), Length(max=64)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Continue")


class LoginVerificationForm(FlaskForm):
    otp = StringField(
        "Enter 6 Digit OTP Sent to your Email",
        validators=[
            Regexp(r'[0-9]{6}', message='Invalid Code')
        ],
    )
    submit = SubmitField("Authenticate")


class ResetPasswordForm(FlaskForm):

    password = StringField(
        "Password", validators=[DataRequired(message="Cannot be Empty"), Password()]
    )

    verify_password = StringField(
        "Retype Password",
        validators=[
            DataRequired(message="Cannot be Empty"),
            EqualTo("password", message="Password Verification Failed"),
        ],
    )

    submit = SubmitField("Reset Password")


class RegisterationUserDetailsForm(FlaskForm):
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(message="Cannot be Empty"),
            Regexp(r"^([a-zA-Z]+\s?){1,}$", message="Invalid First Name"),
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(message="Cannot be Empty"),
            Regexp(r"^([a-zA-Z]+\s?){1,}$", message="Invalid Second Name"),
        ],
    )

    dob = DateField(
        "Date of Birth", validators=[DataRequired(message="Cannot be Empty"), Date()]
    )

    gender = RadioField(
        "Gender", choices=["Male", "Female"], validators=[InputRequired()]
    )

    email = EmailField(
        "Email",
        validators=[email(message="Invalid Email"), DataRequired()],
        
    )

    phone_number = StringField(
        "Phone Number",
        validators=[
            DataRequired(message="Cannot be Empty"),
            Regexp(r"^(\+94|0)[0-9]{9}$"),
            PhoneNumber(action="VALIDATE"),
        ],
    )

    submit = SubmitField("Next")


class RegistretionUserCredentialsForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[DataRequired(message="Cannot be Empty"), UsernameAvailable()],
    )

    password = StringField(
        "Password", validators=[DataRequired(message="Cannot be Empty"), Password()]
    )

    verify_password = StringField(
        "Retype Password",
        validators=[
            DataRequired(message="Cannot be Empty"),
            EqualTo("password", message="Password Verification Failed"),
        ],
    )

    submit = SubmitField("Register")
