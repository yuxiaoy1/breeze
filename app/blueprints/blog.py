from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy import select
from sqlalchemy.orm import with_parent

from app.email import send_new_comment_email, send_new_reply_email
from app.extensions import db
from app.forms import AdminCommentForm, CommentForm
from app.models import Category, Comment, Post
from app.utils import redirect_back

blog = Blueprint("blog", __name__)


@blog.get("/")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["POST_PER_PAGE"]
    pagination = db.paginate(
        select(Post).order_by(Post.created_at.desc()), page=page, per_page=per_page
    )
    posts = pagination.items
    return render_template("blog/index.html", pagination=pagination, posts=posts)


@blog.get("/about")
def about():
    return render_template("blog/about.html")


@blog.get("/categories/<int:id>")
def show_category(id):
    category = db.get_or_404(Category, id)
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["POST_PER_PAGE"]
    pagination = db.paginate(
        select(Post)
        .filter(with_parent(category, Category.posts))
        .order_by(Post.created_at.desc()),
        page=page,
        per_page=per_page,
    )
    posts = pagination.items
    return render_template(
        "blog/category.html", category=category, pagination=pagination, posts=posts
    )


@blog.route("/posts/<int:id>", methods=["GET", "POST"])
def show_post(id):
    post = db.get_or_404(Post, id)
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["COMMENT_PER_PAGE"]
    pagination = db.paginate(
        select(Comment)
        .filter(with_parent(post, Post.comments))
        .filter_by(reviewed=True)
        .order_by(Comment.created_at.asc()),
        page=page,
        per_page=per_page,
    )
    comments = pagination.items
    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.daat = current_user.name
        form.email.data = current_app.config["ADMIN_EMAIL"]
        form.site.data = url_for(".index", _external=True)
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False
    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author,
            email=email,
            site=site,
            body=body,
            from_admin=from_admin,
            post_id=id,
            reviewed=reviewed,
        )
        replied_id = request.args.get("reply")
        if replied_id:
            replied_comment = db.get_or_404(Comment, replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)
        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:
            flash("Comment published.", "success")
        else:
            flash("Thanks, your comment will be published after reviewed.", "info")
            send_new_comment_email(post)
        return redirect(url_for(".show_post", id=id))
    return render_template(
        "blog/post.html", post=post, pagination=pagination, comments=comments, form=form
    )


@blog.get("/reply/comment/<int:id>")
def reply_comment(id):
    comment = db.get_or_404(Comment, id)
    if not comment.post.can_comment:
        flash("Comment is disabled.", "warning")
        return redirect(url_for(".show_post", id=comment.post.id))
    return redirect(
        url_for(".show_post", id=comment.post_id, reply=id, author=comment.author)
        + "#comment-form"
    )


@blog.get("/change-theme/<theme_name>")
def change_theme(theme_name):
    if theme_name not in current_app.config["THEMES"]:
        abort(400, description="Invalid theme name")
    response = make_response(redirect_back())
    response.set_cookie("theme", theme_name, max_age=30 * 24 * 60 * 60)
    return response
