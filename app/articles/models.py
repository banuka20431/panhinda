from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import ForeignKey, String, update
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app import db
from app.auth.models import User


class Article(db.Model):

    __tablename__ = "article"

    id: Mapped[int] = mapped_column(primary_key=True)

    author_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), index=True, nullable=False
    )

    title: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)

    description: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)

    body: Mapped[str] = mapped_column(String(12288))

    created: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    edited: Mapped[Optional[datetime]] = mapped_column(index=True, nullable=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id"), index=True, nullable=False
    )

    # relationships

    author: Mapped["User"] = relationship(back_populates="articles")
    category: Mapped["Category"] = relationship(back_populates="articles")
    likes: Mapped[list["Like"]] = relationship(back_populates="article")
    comments: Mapped[list["Comment"]] = relationship(back_populates="article")

    def __repr__(self):
        return f"<Post '{self.id} - {self.title}'>"

    def __init__(
        self, author_id: int, title: str, description: str, body: str, category_id: int
    ):
        self.author_id = author_id
        self.title = title
        self.description = description
        self.body = body
        self.created = datetime.now(timezone.utc)
        self.category_id = category_id

    def to_dict(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "title": self.title,
            "description": self.description,
            "body": self.body,
            "created": self.created.isoformat() if self.created else None,
            "edited": self.edited.isoformat() if self.edited else None,
            "category_id": self.category_id,
        }


class Category(db.Model):

    __tablename__ = "category"

    # columns

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(32))

    # relationships

    sub_categories: Mapped[list["SubCategory"]] = relationship(
        back_populates="category_belonged"
    )

    interested_users: Mapped[list["UserInterest"]] = relationship(
        back_populates="category"
    )

    articles: Mapped[list["Article"]] = relationship(back_populates="category")

    def __repr__(self):
        return f"<Category '{self.id} - {self.label}'>"

    def __init__(self, label):
        self.label = label

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
        }


class SubCategory(db.Model):

    __tablename__ = "sub_category"

    # columns

    id: Mapped[int] = mapped_column(primary_key=True)

    label: Mapped[str] = mapped_column(String(32))

    category_id: Mapped[str] = mapped_column(
        ForeignKey("category.id"), index=True, nullable=False
    )

    # relationships

    category_belonged: Mapped["Category"] = relationship(
        back_populates="sub_categories"
    )

    def __repr__(self):
        return f"<Sub Category '{self.id} - {self.label}'>"

    def __init__(self, label: str, category_id: int):
        self.label = label
        self.category_id = category_id

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "category_id": self.category_id,
        }


class Like(db.Model):

    __tablename__ = "like"

    # columns

    id: Mapped[int] = mapped_column(primary_key=True)

    article_id: Mapped[int] = mapped_column(ForeignKey("article.id"))

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    added: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    # relationships

    user: Mapped["User"] = relationship(back_populates="liked_articles")
    article: Mapped["Article"] = relationship(back_populates="likes")

    def __init__(self, article_id, user_id):
        self.article_id = article_id
        self.user_id = user_id

    def to_dict(self):
        return {
            "id": self.id,
            "article_id": self.article_id,
            "user_id": self.user_id,
            "added": self.added.isoformat() if self.added else None,
        }


class Comment(db.Model):

    __tablename__ = "comment"

    # columns

    id: Mapped[int] = mapped_column(primary_key=True)

    body: Mapped[str] = mapped_column(String(1024), nullable=False)

    created: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )

    edited: Mapped[Optional[datetime]] = mapped_column(index=True, nullable=True)

    article_id: Mapped[int] = mapped_column(ForeignKey("article.id"))

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    # relationships

    user: Mapped["User"] = relationship(back_populates="commented_articles")
    article: Mapped["Article"] = relationship(back_populates="comments")

    def __init__(self, body: str, article_id: int, user_id: int):
        self.body = body
        self.article_id = article_id
        self.user_id = user_id

    def to_dict(self):
        return {
            "id": self.id,
            "body": self.body,
            "created": self.created.isoformat() if self.created else None,
            "edited": self.edited.isoformat() if self.edited else None,
            "article_id": self.article_id,
            "user_id": self.user_id,
        }
