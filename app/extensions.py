from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mailman import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

ckeditor = CKEditor()
db = SQLAlchemy()
bootstrap = Bootstrap5()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()


@login_manager.user_loader
def load_user(id):
    from app.models import Admin

    user = db.session.get(Admin, id)
    return user


login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
