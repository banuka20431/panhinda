from flask_wtf import FlaskForm  # type: ignore
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import Length

from app import db
from app.articles.models import SubCategory


from sqlalchemy import select


class CreateArticleForm(FlaskForm):

    title = StringField(
        "Article Title",
        validators=[
            Length(
                min=5, max=120, message="Title should be between 5 to 120 characters"
            ),
        ],
        render_kw={"placeholder": "title of your article..."},
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
        render_kw={"placeholder": "what is it about?...", "rows": 3, "cols": 30},
    )
    category = SelectField("Choose a suitable category")

    body = TextAreaField("Article Body", id="body")

    submit = SubmitField("Publish")

    def __init__(self, *args, **kwargs): # type: ignore

        super().__init__(*args, **kwargs).__init__() # type: ignore

        res = db.session.scalars(select(SubCategory)).all() or []

        self.category.choices = [category.label for category in res]  # type: ignore
