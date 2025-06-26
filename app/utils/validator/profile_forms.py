from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField
from wtforms import EmailField, BooleanField, SubmitField, DateField, SelectMultipleField
from wtforms.validators import Length, EqualTo, DataRequired, InputRequired, Regexp
from wtforms.validators import email
from flask_login import current_user

from app.utils.validator.custom_validators import *
from app.utils.validator.auth_forms import RegisterationUserDetailsForm
from app import db, app
from app.auth.models import UserInterest
from app.articles.models import Category


class PersonalInformationForm(RegisterationUserDetailsForm):
    username = StringField("Username", validators=[UsernameAvailable()])
    submit = SubmitField("Update")


class AddInterestsForm(FlaskForm):

    interests = SelectMultipleField('Select Your Interests')
    submit = SubmitField("Add")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        current_user_interested_categories = db.session.scalars(select(UserInterest.category_id).where(UserInterest.user_id==current_user.id)).all()
        categories = db.session.scalars(select(Category)).all()

        self.interests.choices = [(interest.id, interest.label) for interest in categories if interest.id not in current_user_interested_categories]

        
# nothing
    