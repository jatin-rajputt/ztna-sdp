import os

os.environ.setdefault("SECRET_KEY", "test-key")

import pytest
from app import create_app


@pytest.fixture
def app():
    app = create_app({"TESTING": True,
                      "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
                      "RATELIMIT_ENABLED": False})
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()