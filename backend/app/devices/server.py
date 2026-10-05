from ..models import Device
def get_device(user_id, device_id):
    """Return the Device if it belongs to this user, else None (prevents IDOR)."""
    if device_id is None:
        return None
    return Device.query.filter_by(id=device_id, user_id=user_id).first()

def is_trusted(device):
    """REGISTERED + COMPLIANT only."""
    return bool(device and device.registration_status == "REGISTERED"
                and device.compliance_status == "COMPLIANT")