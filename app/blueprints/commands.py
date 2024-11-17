import click
from flask import Blueprint

from app.extensions import db
from app.fake import (
    fake_admin,
    fake_categories,
    fake_comments,
    fake_links,
    fake_posts,
    fake_replies,
)

commands = Blueprint("commands", __name__, cli_group=None)


@commands.cli.command()
def initdb():
    """Create database."""
    db.drop_all()
    db.create_all()
    print("Database created.")


@commands.cli.command()
@click.option("--category", default=5, help="Quantity of categories, default is 10.")
@click.option("--post", default=50, help="Quantity of posts, default is 50.")
@click.option("--comment", default=500, help="Quantity of comments, default is 500.")
@click.option("--reply", default=50, help="Quantity of replies, default is 50.")
def fake(category, post, comment, reply):
    """Generate fake data."""
    db.drop_all()
    db.create_all()

    fake_admin()
    print("Generated the admin.")

    fake_categories(category)
    print(f"Generated {category} categories.")

    fake_posts(post)
    print(f"Generated {post} posts.")

    fake_comments(comment)
    print(f"Generated {comment} comments.")

    fake_replies(reply)
    print(f"Generated {reply} replies.")

    fake_links()
    print("Generated links.")
