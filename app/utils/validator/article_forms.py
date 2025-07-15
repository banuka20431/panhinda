from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import Length

from app import app, db
from app.articles.models import SubCategory, Article, Category


from sqlalchemy import select


class CreateArticleForm(FlaskForm):

    title = StringField(
        "Article Title",
        validators=[
            Length(
                min=5, max=120, message="Title should be between 5 to 120 characters"
            ),
        ],
        render_kw={'placeholder': 'title of your article...'}
    )

    description = TextAreaField(
        "Article Description",
        validators=[
            Length(
                min=5,
                max=250,
                message="Description should be between 5 to 250 characters",
            ),
        ],
        render_kw={'placeholder': 'what is it about?...', 'rows': 3, 'cols': 30}
    )
    category = SelectField("Choose a suitable category")

    body = TextAreaField("Article Body", id="body")

    submit = SubmitField("Publish")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.category.choices = [category.label for category in db.session.scalars(select(SubCategory)).all()]
        