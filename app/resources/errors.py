from functools import wraps
from typing import Optional, Callable, Union, Any

from app import wrapper
from models.device import Device
from schemes import device_not_found, permission_denied, device_powered_off


class MicroserviceException(Exception):
    def __init__(self, error: dict):
        self.error: dict = error


def register_errors(*errors: Callable) -> Callable[[Callable], Callable[[dict, str], dict]]:
    def deco(f: Callable) -> Callable[[dict, str], dict]:
        @wraps(f)
        def inner(data: dict, user: str) -> dict:
            args: tuple = (data, user)
            for func in errors:
                try:
                    result: Union[tuple, Any] = func(*args)
                except MicroserviceException as exception:
                    return exception.error

                if not isinstance(result, tuple):
                    result: tuple = (result,)
                args: tuple = (data, user, *result)

            return f(*args)

        inner.__errors__ = errors

        return inner

    return deco


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
