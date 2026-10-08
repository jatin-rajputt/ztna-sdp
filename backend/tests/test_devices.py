import pytest
from app import db
from app.models import User, Device
from app.devices.service import get_device, is_trusted


@pytest.fixture
def data(app):
    u1 = User(username="dev_a", password_hash="x")
    u2 = User(username="dev_b", password_hash="x")
    db.session.add_all([u1, u2])
    db.session.flush()
    good = Device(user_id=u1.id, registration_status="REGISTERED",
                  compliance_status="COMPLIANT")
    bad = Device(user_id=u1.id)        # defaults: UNKNOWN + NON_COMPLIANT
    db.session.add_all([good, bad])
    db.session.commit()
    return u1, u2, good, bad


def test_registered_compliant_is_trusted(data):
    assert is_trusted(data[2])


def test_unknown_device_not_trusted(data):
    assert not is_trusted(data[3])


def test_none_device_not_trusted():
    assert not is_trusted(None)


def test_cannot_use_another_users_device(data):      # IDOR protection
    u1, u2, good, _ = data
    assert get_device(u1.id, good.id) is good
    assert get_device(u2.id, good.id) is None