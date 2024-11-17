from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_ckeditor import upload_fail, upload_success
from flask_login import current_user, login_required
from sqlalchemy import select

from app.extensions import db
from app.forms import EditCategoryForm, LinkForm, NewCategoryForm, PostForm, SettingForm
from app.models import Category, Comment, Link, Post
from app.utils import allowed_file, random_filename, redirect_back

admin = Blueprint("admin", __name__)


@admin.before_request
@login_required
def before_admin_request():
    pass


@admin.route("/settings", methods=["GET", "POST"])
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.blog_title = form.blog_title.data
        current_user.blog_subtitle = form.blog_subtitle.data
        current_user.about = form.about.data
        current_user.custom_footer = form.custom_footer.data
        current_user.custom_css = form.custom_css.data
        current_user.custom_js = form.custom_js.data
        db.session.commit()
        flash("Setting updated.", "success")
        return redirect(url_for("blog.index"))
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_subtitle.data = current_user.blog_subtitle
    form.about.data = current_user.about
    form.custom_footer.data = current_user.custom_footer
    form.custom_css.data = current_user.custom_css
    form.custom_js.data = current_user.custom_js
    return render_template("admin/settings.html", form=form)


@admin.get("/posts/manage")
def manage_post():
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["MANAGE_POST_PER_PAGE"]
    pagination = db.paginate(
        select(Post).order_by(Post.created_at.desc()),
        page=page,
        per_page=per_page,
        error_out=False,
    )
    if page > pagination.pages:
        return redirect(url_for(".manage_post", page=pagination.pages))
    posts = pagination.items
    return render_template(
        "admin/manage_post.html", page=page, pagination=pagination, posts=posts
    )


@admin.route("/posts/new", methods=["GET", "POST"])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category_id = form.category.data
        post = Post(title=title, body=body, category_id=category_id)
        db.session.add(post)
        db.session.commit()
        flash("Post created.", "success")
        return redirect(url_for("blog.show_post", id=post.id))
    return render_template("admin/new_post.html", form=form)


@admin.route("/posts/<int:id>/edit", methods=["GET", "POST"])
def edit_post(id):
    form = PostForm()
    post = db.get_or_404(Post, id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category_id = form.category.data
        db.session.commit()
        flash("Post updated.", "success")
        return redirect(url_for("blog.show_post", id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template("admin/edit_post.html", form=form)


@admin.post("/posts/<int:id>/delete")
def delete_post(id):
    post = db.get_or_404(Post, id)
    post.delete()
    flash("Post deleted.", "success")
    return redirect_back()


@admin.post("/posts/<int:id>/set-comment")
def set_comment(id):
    post = db.get_or_404(Post, id)
    if post.can_comment:
        post.can_comment = False
        flash("Comment disabled.", "success")
    else:
        post.can_comment = True
        flash("Comment enabled.", "success")
    db.session.commit()
    return redirect_back()


@admin.get("/comments/manage")
def manage_comment():
    filter = request.args.get("filter", "all")
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config["COMMENT_PER_PAGE"]
    if filter == "unread":
        filtered_commnets = select(Comment).filter_by(reviewed=False)
    elif filter == "admin":
        filtered_commnets = select(Comment).filter_by(from_admin=True)
    else:
        filtered_commnets = select(Comment)
    pagination = db.paginate(
        filtered_commnets.order_by(Comment.created_at.desc()),
        page=page,
        per_page=per_page,
        error_out=False,
    )
    if page > pagination.pages:
        return redirect(
            url_for(".manage_comment", page=pagination.pages, filter=filter)
        )
    comments = pagination.items
    return render_template(
        "admin/manage_comment.html", comments=comments, pagination=pagination
    )


@admin.post("/comments/<int:id>/approve")
def approve_comment(id):
    comment = db.get_or_404(Comment, id)
    comment.reviewed = True
    db.session.commit()
    flash("Comment published.", "success")
    return redirect_back()


@admin.post("/comments/approve")
def approve_all_comment():
    comments = db.session.scalars(select(Comment).filter_by(reviewed=False))
    for comment in comments:
        comment.reviewed = True
    db.session.commit()
    flash("All comments published.", "success")
    return redirect_back()


@admin.post("/comments/<int:id>/delete")
def delete_comment(id):
    comment = db.get_or_404(Comment, id)
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted.", "success")
    return redirect_back()


@admin.get("/categories/manage")
def manage_category():
    return render_template("admin/manage_category.html")


@admin.route("/categories/new", methods=["GET", "POST"])
def new_category():
    form = NewCategoryForm()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash("Category created.", "success")
        return redirect(url_for(".manage_category"))
    return render_template("admin/new_category.html", form=form)


@admin.route("/categories/<int:id>/edit", methods=["GET", "POST"])
def edit_category(id):
    category = db.get_or_404(Category, id)
    if category.id == 1:
        flash("You can not edit the default category", "warning")
        return redirect(url_for("blog.index"))
    form = EditCategoryForm(current_name=category.name)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash("Category updated.", "success")
        return redirect(url_for(".namage_category"))
    form.name.data = category.name
    return render_template("admin/edit_category.html", form=form)


@admin.post("/categories/<int:id>/delete")
def delete_category(id):
    category = db.get_or_404(Category, id)
    if category.id == 1:
        flash("You can not delete the default category", "warning")
        return redirect(url_for("blog.index"))
    category.delete()
    flash("Category deleted.", "success")
    return redirect(url_for(".manage_category"))


@admin.get("/links/manage")
def manage_link():
    return render_template("admin/manage_link.html")


@admin.route("/links/new", methods=["GET", "POST"])
def new_link():
    form = LinkForm()
    if form.validate_on_submit():
        name = form.name.data
        url = form.url.data
        link = Link(name=name, url=url)
        db.session.add(link)
        db.session.commit()
        flash("Link created.", "success")
        return redirect(url_for(".manage_link"))
    return render_template("admin/new_link.html", form=form)


@admin.route("/links/<int:id>/edit", methods=["GET", "POST"])
def edit_link(id):
    form = LinkForm()
    link = db.get_or_404(Link, id)
    if form.validate_on_submit():
        link.name = form.name.data
        link.url = form.url.data
        db.session.commit()
        flash("Link updated.", "succes")
        return redirect(url_for(".manage_link"))
    form.name.data = link.name
    form.url.data = link.url
    return render_template("admin/edit_link.html", form=form)


@admin.post("/links/<int:id>/delete")
def delete_link(id):
    link = db.get_or_404(Link, id)
    db.session.delete(link)
    db.session.commit()
    flash("Link deleted.", "success")
    return redirect(url_for(".namage_link"))


@admin.post("/upload")
def upload_image():
    f = request.files.get("upload")
    if not allowed_file(f.filename):
        return upload_fail("Image only!")
    filename = random_filename(f.filename)
    f.save()
    url = url_for("blog.get_image", filename=filename)
    return upload_success(url, filename)
