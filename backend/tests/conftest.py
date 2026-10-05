import os

os.environ.setdefault("SECRET_KEY", "test-key")

import pytest
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    app = create_app({"TESTING": True,
                      "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                      "RATELIMIT_ENABLED": False})
    with app.app_context():
        db.session.add(User(username="alice",
                            password_hash=generate_password_hash("Pass1234!")))
        db.session.commit()
        yield app


@pytest.fixture
def client(app):
    return app.test_client()