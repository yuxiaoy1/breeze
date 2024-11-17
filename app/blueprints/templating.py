from flask import Blueprint
from flask_login import current_user
from sqlalchemy import func, select

from app.extensions import db
from app.models import Admin, Category, Comment, Link

templating = Blueprint("templating", __name__)


@templating.app_context_processor
def make_template_context():
    admin = db.session.scalar(select(Admin))
    categories = db.session.scalars(select(Category).order_by(Category.name)).all()
    links = db.session.scalars(select(Link).order_by(Link.name)).all()
    unread_comments = None
    if current_user.is_authenticated:
        unread_comments = db.session.scalar(
            select(func.count(Comment.id)).filter_by(reviewed=False)
        )
    return dict(
        admin=admin, categories=categories, links=links, unread_comments=unread_comments
    )
