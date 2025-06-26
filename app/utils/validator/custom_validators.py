from wtforms import ValidationError

from re import DOTALL, compile
from datetime import datetime
from typing import Literal
from sqlalchemy import select

from app.utils.func import get_sha256_hash
from app import app, db
from app.auth.models import User

from typing import Any

class Date:

    def __init__(self, min_age: int = 4):
        self.min_age = min_age

    def __call__(self, form, field):

        validation_state = True
        pattern = compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")

        if not pattern.fullmatch(field.data.__str__()):
            validation_state = False
        else:
            ret = pattern.findall(field.data.__str__())[0]
            year, month, day = [int(item) for item in ret]
            present_year = datetime.now().strftime(r"%Y")

            months_31 = (1, 3, 5, 7, 8, 10, 12)
            months_30 = (4, 6, 9, 11)

            if (int(present_year) - year) <= self.min_age:
                raise ValidationError("Age restricted to a minimum of four years")

            if (month in months_31) and not (0 < day < 32):
                validation_state = False

            if (month in months_30) and not (0 < day < 31):
                validation_state = False

            if month == 2:
                if year % 4 == 0:
                    if not day <= 29:
                        validation_state = False
                else:
                    if not day <= 28:
                        validation_state = False

        if not validation_state:

            raise ValidationError("Invalid Date")


class UsernameAvailable:

    def __call__(self, form, field):
        query = select(User.username).where(User.username == field.data)
        if db.session.scalar(query) is not None:
            raise ValidationError(message="Username Not Available")
        

class CheckUsername:

    def __call__(self, form, field):
        user: User = db.session.scalar(
            select(User.username).where(User.username == field.data)
        )
        if not user:
            raise ValidationError(message="User Not Found")

class Password:

    def __init__(self):
        self.short_pwd_pattern = compile(r"^.{0,7}$", flags=DOTALL)
        self.weak_pwd_patterns = (
            compile(r"^[a-zA-Z0-9_]+$"),
            compile(r"^[a-zA-Z\W_]+$"),
            compile(r"^[a-z\W_]+$"),
            compile(r"^[A-Z\W_]+$"),
            compile(r"^[0-9\W_]+$"),
        )

    def __call__(self, form, field):
        if self.short_pwd_pattern.fullmatch(field.data) is not None:
            raise ValidationError(message="Password must have atleast 8 characters")

        for pattern in self.weak_pwd_patterns:
            if pattern.fullmatch(field.data) is not None:
                raise ValidationError(message="Weak password")


class PhoneNumber:
    """
    Validate phone numbers
    Detect pre registered phone numbers
    Phone Number Verification
    """

    def __init__(
        self,
        userid: int | None = None,
        action: Literal["VALIDATE", "VERIFY"] = "VALIDATE",
    ):
        self.action = action
        self.userid = userid

    def __call__(self, form, field):
        self.hashed_phone_number = get_sha256_hash(field.data)

        match self.action:
            case "VALIDATE":
                self.validate()
            case "VERIFY":
                self.verify()

    def validate(self):
        query = select(User.phone_number).where(
            User.phone_number == self.hashed_phone_number
        )
        if db.session.scalar(query) is not None:
            raise ValidationError(message="Phone Number Already Registered")

    def verify(self):
        if self.userid is None:
            raise ValidationError(message="Server Error Occurred")
        else:
            query = select(User.phone_number).where(User.id == self.userid)
            if self.hashed_phone_number != db.session.scalar(query):
                raise ValidationError(message="Phone Number Doesn't Match")

class Unique:

    def __init__(self, model: Any, attr: str):
        with app.app_context():
           self.used_attr_values = [article.to_dict()[attr] for article in db.session.scalars(select(model)).all()]
           
    def __call__(self, form, field):
        if field.data in self.used_attr_values:
            raise ValidationError(message=f"{field.label} is already have used by someone")