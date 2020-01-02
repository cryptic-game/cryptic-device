from typing import Optional

from app import wrapper
from cryptic import MicroserviceException
from models.device import Device
from schemes import device_not_found, permission_denied, device_powered_off


def device_exists(data: dict, user: str) -> Device:
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        raise MicroserviceException(device_not_found)

    return device


def can_access_device(data: dict, user: str, device: Device) -> Device:
    if not device.check_access(user):
        raise MicroserviceException(permission_denied)

    return device


def device_powered_on(data: dict, user: str, device: Device) -> Device:
    if not device.powered_on:
        raise MicroserviceException(device_powered_off)

    return device
