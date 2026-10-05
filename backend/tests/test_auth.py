from app.models import User, AuditLog


def login(c, pw):
    return c.post("/api/auth/login", json={"username": "alice", "password": pw})


def test_login_success(client):
    assert login(client, "Pass1234!").status_code == 200
    assert client.get("/api/auth/me").status_code == 200


def test_invalid_credentials(client):
    assert login(client, "wrong").status_code == 401
    assert client.get("/api/auth/me").status_code == 401


def test_password_not_plaintext(client):
    assert User.query.filter_by(username="alice").first().password_hash != "Pass1234!"


def test_lockout_after_5_failures(client):
    for _ in range(5):
        login(client, "wrong")
    assert login(client, "Pass1234!").status_code == 401   # locked even with the right password
    assert AuditLog.query.filter_by(event="BRUTE_FORCE_DETECTED").count() == 1


def test_logout_ends_session(client):
    login(client, "Pass1234!")
    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").status_code == 401