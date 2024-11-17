from flask import Flask

from app.blueprints.admin import admin
from app.blueprints.auth import auth
from app.blueprints.blog import blog
from app.blueprints.commands import commands
from app.blueprints.errors import errors
from app.blueprints.templating import templating
from app.config import config
from app.extensions import bootstrap, ckeditor, csrf, db, login_manager, mail


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # extensions
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    ckeditor.init_app(app)

    # blueprints
    app.register_blueprint(commands)
    app.register_blueprint(errors)
    app.register_blueprint(templating)
    app.register_blueprint(blog)
    app.register_blueprint(auth)
    app.register_blueprint(admin)

    return app
