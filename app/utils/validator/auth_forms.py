from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField
from wtforms import EmailField, BooleanField, SubmitField, DateField
from wtforms.validators import Length, EqualTo, DataRequired, InputRequired, Regexp
from wtforms.validators import email

from app.utils.validator.custom_validators import *


class RegisterationUserDetailsForm(
    FlaskForm
):  # Handles basic user details when registering
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(message="First Name Cannot be Empty"),
            Regexp(r"^([a-zA-Z]+\s?){1,}$", message="Invalid First Name"),
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(message="Last Name Cannot be Empty"),
            Regexp(r"^([a-zA-Z]+\s?){1,}$", message="Invalid Second Name"),
        ],
    )

    dob = DateField(
        "Date of Birth", validators=[DataRequired(message="Cannot be Empty"), Date()]
    )

    gender = RadioField(
        "Gender",
        choices=["Male", "Female"],
        validators=[InputRequired(message="Please Choose a Gender")],
    )

    email = EmailField(
        "Email",
        validators=[
            email(message="Invalid Email"),
            DataRequired(message="Email Cannot be Empty"),
        ],
    )

    phone_number = StringField(
        "Phone Number",
        validators=[
            DataRequired(message="Phone Number Cannot be Empty"),
            Regexp(r"^(\+94|0)[0-9]{9}$", message="Invalid Phone Number"),
            PhoneNumber(action="VALIDATE"),
        ],
    )

    submit = SubmitField("Next")


class RegistretionUserCredentialsForm(
    FlaskForm
):  # Handles user credentials when registering

    username = StringField(
        "Username",
        validators=[DataRequired(message="Cannot be Empty"), UsernameAvailable()],
    )

    password = PasswordField(
        "Password", validators=[DataRequired(message="Cannot be Empty"), Password()]
    )

    verify_password = PasswordField(
        "Retype Password",
        validators=[
            DataRequired(message="Cannot be Empty"),
            EqualTo("password", message="Password Verification Failed"),
        ],
    )

    submit = SubmitField("Register")


class EmailConfirmationResendForm(
    FlaskForm
):  # Handles resending email confirmation link
    username = StringField(
        "Username",
        validators=[DataRequired(message="Cannot be Empty"), CheckUsername()],
    )

    email = EmailField(
        "Email",
        validators=[
            email(message="Invalid Email"),
            DataRequired(message="Email Cannot be Empty"),
        ],
    )

    submit = SubmitField("Send")


class LoginForm(FlaskForm):  # Handles user login
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username Cannot be Empty"),
            Length(max=32),
            CheckUsername(),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(message="Enter Password"),
            Length(max=64, message="Password Maximum Character Length Exceeded"),
        ],
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Continue")


class LoginVerificationForm(FlaskForm):  # Handles user verification when login
    otp = StringField(
        "Enter 6 Digit OTP Sent to your Email",
        validators=[Regexp(r"[0-9]{6}", message="Invalid Code")],
    )
    submit = SubmitField("Authenticate")


class ResetPasswordForm(
    FlaskForm
):  # Handles password resetting when user isn't logged in

    email = EmailField(
        "Email",
        validators=[
            email(message="Invalid Email"),
            DataRequired(message="Email Cannot be Empty"),
        ],
    )

    password = PasswordField(
        "New Password", validators=[DataRequired(message="Cannot be Empty"), Password()]
    )

    verify_password = PasswordField(
        "Retype Password",
        validators=[
            DataRequired(message="Cannot be Empty"),
            EqualTo("password", message="Password Verification Failed"),
        ],
    )

    submit = SubmitField("Verify Details")


class PasswordResetUserVerificationForm(LoginVerificationForm): 
    pass  # Handles user verification while password resetting when user isn't logged in


class LogonResetPasswordForm(
    FlaskForm
):  # Handles password resetting when user is logged in

    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password Cannot be Empty"), Password()],
    )

    verify_password = PasswordField(
        "Retype your password",
        validators=[
            DataRequired(message="Password Verification Failed"),
            EqualTo("password", message="Password Verification Failed"),
        ],
    )

    submit = SubmitField("Reset Password")
