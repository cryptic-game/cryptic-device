from typing import List, Optional, Dict, Any
from objects import session
from models.device import Device
from app import m


# ENDPOINTS FOR HANDLE #


@m.user_endpoint(path=["device", "public_info"])
def public_info(data: dict, user: str) -> dict:
    """
    Get public information about a device.
    :param data:
    :param user:
    :return: The response
    """
    device: Optional[Device] = session.query(Device).filter_by(uuid=data["device_uuid"]).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    return device.serialize


@m.user_endpoint(path=["device", "private_info"])
def private_info(data: dict, user: str) -> dict:
    """
    Get private information about a device.
    :param user:
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(user):
        return {
            'ok': False,
            'error': 'no access to this device'
        }

    return device.serialize


@m.user_endpoint(path=["device", "ping"])
def ping(data: dict, user: str) -> dict:
    """
    Ping a device.
    :param data:
    :param user:
    :return: The response
    """
    device: Optional[Device] = session.query(Device).filter_by(uuid=data["device_uuid"]).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    return {
        "online": device.powered_on
    }


@m.user_endpoint(path=["device", "all"])
def get_all(data: dict, user: str) -> dict:
    """
    Get all devices
    :param data:
    :param user:
    :return: The response
    """
    devices: List[Device] = session.query(Device).filter_by(owner=data["user_uuid"]).all()

    return {
        "devices": [d.serialize for d in devices]
    }


@m.user_endpoint(path=["device", "create"])
def create(data: dict, user: str) -> dict:
    """
    Create a device.
    :param data:
    :param user:
    :return: The response
    """
    device_count = session.query(Device).filter_by(owner=data["user_uuid"]).first()

    if device_count:
        return {
            'ok': False,
            'error': 'you already own a device'
        }

    device: Device = Device.create(data["user_uuid"], 1, True)

    return device.serialize


@m.user_endpoint(path=["device", "power"])
def power(data: dict, user: str) -> dict:
    """
    Turn a device on/off.
    :param user:
    :param data: The given data
    :return: The response
    """
    device: Device = session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(user):
        return {
            'ok': False,
            'error': 'no access to this device'
        }

    device.powered_on: bool = not device.powered_on
    session.commit()

    return device.serialize


@m.user_endpoint(path=["device", "change_name"])
def change_name(data: dict, user: str) -> dict:
    """
    Change the name of the device.
    :param user:
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(user):
        return {
            'ok': False,
            'error': 'no access to this device'
        }

    try:
        name: str = str(data['name'])
    except KeyError:
        return {
            'ok': False,
            'error': 'no name given'
        }

    device.name: str = name

    session.commit()

    return device.serialize


@m.user_endpoint(path=["device", "delete"])
def delete(data: dict, user: str) -> dict:
    """
    Delete a device.
    :param user:
    :param data: The given data
    :return: The response
    """
    device: Device = session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(user):
        return {
            'ok': False,
            'error': 'no access to this device'
        }

    session.delete(device)
    session.commit()

    return {"ok": True}


@m.microservice_endpoint(path=["exist"])
def exist(data: dict, microservice: str) -> dict:
    """
    Does a device exist?
    :param data:
    :param microservice:
    :return: True or False
    """
    device: Optional[Device] = session.query(Device).filter_by(uuid=data["device_uuid"]).first()

    return {
        'exists': device is not None
    }
