import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)


def create_app(test_config=None):
    app = Flask(__name__, template_folder="../../frontend/templates",
                static_folder="../../frontend/static")
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///ztna.db")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    if test_config:
        app.config.update(test_config)
    db.init_app(app)
    limiter.init_app(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # ---- JATIN's blueprints (auth, mfa, users, access, sessions) ----

    # ---- KOMAL's blueprints (devices, policies, audit, dashboard) ----

    with app.app_context():
        from . import models  # noqa: F401
        db.create_all()
    return app