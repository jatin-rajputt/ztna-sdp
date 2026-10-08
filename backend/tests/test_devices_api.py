from app import db
from app.models import Device
from app.devices.service import is_trusted, posture_ok
from conftest import PASSWORD


def login(c, user):
    return c.post("/api/auth/login", json={"username": user, "password": PASSWORD})


def register(c, host="alice-pc", os_name="Windows 10"):
    return c.post("/api/devices/register",
                  json={"hostname": host, "operating_system": os_name})


def test_requires_login(client):
    assert client.get("/api/devices").status_code == 401


def test_new_device_is_untrusted(client):
    login(client, "alice")
    r = register(client)
    assert r.status_code == 201
    body = r.get_json()
    assert body["registration_status"] == "UNKNOWN"
    assert body["compliance_status"] == "NON_COMPLIANT"


def test_bad_hostname_rejected(client):
    login(client, "alice")
    assert register(client, host="a b;rm -rf").status_code == 400


def test_user_sees_only_own_devices(client, admin_client):
    register(admin_client, host="boss-pc")
    login(client, "alice")
    register(client, host="alice-pc")
    hosts = [d["hostname"] for d in client.get("/api/devices").get_json()]
    assert hosts == ["alice-pc"]


def test_employee_cannot_approve(client):
    login(client, "alice")
    dev_id = register(client).get_json()["id"]
    r = client.patch(f"/api/devices/{dev_id}", json={"approve": True})
    assert r.status_code == 403


def test_admin_approval_makes_device_trusted(client, admin_client):
    login(client, "alice")
    dev_id = register(client).get_json()["id"]
    assert admin_client.patch(f"/api/devices/{dev_id}",
                              json={"approve": True}).status_code == 200
    db.session.expire_all()
    assert is_trusted(db.session.get(Device, dev_id))


def test_unsupported_os_stays_non_compliant(client, admin_client):
    login(client, "alice")
    dev_id = register(client, os_name="Windows XP").get_json()["id"]
    admin_client.patch(f"/api/devices/{dev_id}", json={"approve": True})
    db.session.expire_all()
    assert not is_trusted(db.session.get(Device, dev_id))


def test_posture_ok_list():
    assert posture_ok("Windows 10")
    assert not posture_ok("Kali")      # the attacker VM can never become trusted