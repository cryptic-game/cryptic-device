from typing import Optional, Tuple

from app import wrapper
from cryptic import MicroserviceException
from models.device import Device
from models.file import File
from schemes import device_not_found, permission_denied, device_powered_off, file_not_found


def device_exists(data: dict, user: str) -> Device:
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        raise MicroserviceException(device_not_found)

    return device


def can_access_device(data: dict, user: str, device: Device) -> Device:
    if not device.check_access(user):
        raise MicroserviceException(permission_denied)

    return device


def is_owner_of_device(data: dict, user: str, device: Device) -> Device:
    if device.owner != user:
        raise MicroserviceException(permission_denied)

    return device


def device_powered_on(data: dict, user: str, device: Device) -> Device:
    if not device.powered_on:
        raise MicroserviceException(device_powered_off)

    return device


def file_exists(data: dict, user: str, device: Device) -> Tuple[Device, File]:
    file: Optional[File] = wrapper.session.query(File).filter_by(device=device.uuid, uuid=data["file_uuid"]).first()

    if file is None:
        raise MicroserviceException(file_not_found)

    return device, file
