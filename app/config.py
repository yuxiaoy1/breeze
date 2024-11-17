import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "top secret!")

    POST_PER_PAGE = 5
    COMMENT_PER_PAGE = 10
    MANAGE_POST_PER_PAGE = 10

    UPLOAD_PATH = os.getenv("UPLOAD_PATH", BASE_DIR / "uploads")
    ALLOWED_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif"]

    THEMES = {
        "default": "Default",
        "cerulean": "Cerulean",
        "cosmo": "Cosmo",
        "cyborg": "Cyborg",
        "darkly": "Darkly",
        "flatly": "Flatly",
        "minty": "Minty",
        "simplex": "Simplex",
        "sketchy": "Sketchy",
        "slate": "Slate",
        "solar": "Solar",
    }


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'db-dev.sqlite'}"
    )
    ADMIN_EMAIL = "frank@example.com"


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite'}"
    )


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
