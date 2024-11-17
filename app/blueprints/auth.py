from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select

from app.extensions import db
from app.forms import LoginForm
from app.models import Admin
from app.utils import redirect_back

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("blog.index"))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        admin = db.session.scalar(select(Admin))
        if admin:
            if username == admin.username and admin.check_password(password):
                login_user(admin, remember)
                flash("Welcome back.", "info")
                return redirect_back()
            flash("Invalid username or password.", "warning")
        else:
            flash("No account found.", "warning")
    return render_template("auth/login.html", form=form)


@auth.get("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout success", "info")
    return redirect_back()
