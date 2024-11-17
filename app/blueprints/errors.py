from flask import Blueprint, render_template
from flask_wtf.csrf import CSRFError

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(400)
def bad_request(error):
    return render_template("errors/400.html", description=error.description), 400


@errors.app_errorhandler(404)
def not_found(error):
    return render_template("errors/404.html", description=error.description), 404


@errors.app_errorhandler(500)
def internal_server_error(error):
    return render_template("errors/500.html", description=error.description), 500


@errors.app_errorhandler(CSRFError)
def crsf_error(error):
    description = "Session expired, return last page and try again."
    return render_template("errors/400.html", description=description), 400
