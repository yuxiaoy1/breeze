import re
from datetime import datetime, timezone

from flask import current_app, url_for
from flask_login import UserMixin
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class Admin(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(String(128))
    blog_title: Mapped[str] = mapped_column(String(60))
    blog_subtitle: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(30))
    about: Mapped[str] = mapped_column(Text)
    custom_footer: Mapped[str | None] = mapped_column(Text)
    custom_css: Mapped[str | None] = mapped_column(Text)
    custom_js: Mapped[str | None] = mapped_column(Text)

    @property
    def password(self):
        raise AttributeError("Write-only property!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    posts: Mapped[list["Post"]] = relationship(back_populates="category")

    def delete(self):
        default_category = db.session.get(Category, 1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(60))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=lambda: datetime.now(timezone.utc)
    )
    can_comment: Mapped[bool] = mapped_column(default=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    category: Mapped["Category"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post", cascade="all,delete-orphan"
    )

    @property
    def reviewed_comments_count(self):
        return len([comment for comment in self.comments if comment.reviewed])

    def delete(self):
        upload_path = current_app.config("UPLOAD_PATH")
        images = self.extract_images()
        for image in images:
            file_path = upload_path / image
            if upload_path.exists():
                file_path.unlink()
        db.session.delete(self)
        db.session.commit()

    def extract_images(self):
        upload_url = url_for("blog.get_image", filename="")
        return re.findall(rf'<img.*?src="{upload_url}(.*?)"', self.body)


class Comment(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(254))
    site: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    from_admin: Mapped[bool] = mapped_column(default=False)
    reviewed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc), index=True
    )
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"))
    post: Mapped["Post"] = relationship(back_populates="comments")
    replied_id: Mapped[int | None] = mapped_column(ForeignKey("comment.id"))
    replied: Mapped["Comment"] = relationship(
        back_populates="replies", remote_side=[id]
    )
    replies: Mapped[list["Comment"]] = relationship(
        back_populates="replied", cascade="all, delete-orphan"
    )


class Link(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    url: Mapped[str] = mapped_column(String(255))