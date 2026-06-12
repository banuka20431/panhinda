from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField
from wtforms import SubmitField, SelectMultipleField
from wtforms.validators import Regexp
from flask_login import current_user # type: ignore

from app.utils.validator.custom_validators import *
from app import db
from app.auth.models import UserInterest
from app.articles.models import Category


class PersonalInformationForm(FlaskForm):
    
    first_name = StringField(
        "First Name",
        validators=[
            Regexp(r"^([a-zA-Z]+\s?){1,}$", message="Invalid First Name"),
        ],
    )

    last_name = StringField(
        "Last Name",
        validators=[
            Regexp(r"^([a-zA-Z]+\s?){1,}$", message="Invalid Second Name"),
        ],
    )

    username = StringField("Username")
    submit = SubmitField("Update")


class AddInterestsForm(FlaskForm):

    interests = SelectMultipleField('Select Your Interests')
    submit = SubmitField("Add")

    def __init__(self, *args, **kwargs): # type: ignore
        super().__init__(*args, **kwargs) # type: ignore

        current_user_interested_categories = db.session.scalars(select(UserInterest.category_id).where(UserInterest.user_id==current_user.id)).all() # type: ignore
        categories = db.session.scalars(select(Category)).all()

        self.interests.choices = [(interest.id, interest.label) for interest in categories if interest.id not in current_user_interested_categories]

    