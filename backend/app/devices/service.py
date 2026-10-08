from ..models import Device

SUPPORTED_OS = {"windows 10", "windows 11", "ubuntu", "debian", "macos"}


def get_device(user_id, device_id):
    """Return the Device only if it belongs to this user (prevents IDOR)."""
    if device_id is None:
        return None
    return Device.query.filter_by(id=device_id, user_id=user_id).first()


def is_trusted(device):
    """REGISTERED + COMPLIANT only."""
    return bool(device and device.registration_status == "REGISTERED"
                and device.compliance_status == "COMPLIANT")


def posture_ok(os_name):
    """Prototype-level posture check: the OS must be on the supported list."""
    return bool(os_name) and os_name.strip().lower() in SUPPORTED_OS