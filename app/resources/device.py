from typing import List, Optional

from app import m, wrapper
from models.device import Device
from models.workload import Workload
from resources.game_content import check_compatible, calculate_power, create_hardware, check_exists, delete
from schemes import *


@m.user_endpoint(path=["device", "info"], requires={"device_uuid": UUID()})
def info(data: dict, user: str) -> dict:
    """
    Get public information about a device.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found

    return device.serialize


@m.user_endpoint(path=["device", "ping"], requires={"device_uuid": UUID()})
def ping(data: dict, user: str) -> dict:
    """
    Ping a device.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).ge(data["device_uuid"])

    if device is None:
        return device_not_found

    return {"online": device.powered_on}


@m.user_endpoint(path=["device", "all"], requires={})
def get_all(data: dict, user: str) -> dict:
    """
    Get all devices
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    devices: List[Device] = wrapper.session.query(Device).filter_by(owner=user).all()

    return {"devices": [d.serialize for d in devices]}


@m.user_endpoint(path=["device", "create"], requires=requirement_build)
def create(data: dict, user: str) -> dict:
    """
    Create a device.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    comp, message = check_compatible(data)
    if not comp:
        return message

    comp, message = check_exists(user, data)
    if not comp:
        return message

    performance: tuple = calculate_power(data)

    device: Device = Device.create(user, True)

    Workload.create(device.uuid, performance)

    create_hardware(data, device.uuid)

    delete(user, data)

    return device.serialize


@m.user_endpoint(path=["device", "power"], requires={"device_uuid": UUID()})
def power(data: dict, user: str) -> dict:
    """
    Turn a device on/off.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Device = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found

    if not device.check_access(user):
        return permission_denied

    device.powered_on: bool = not device.powered_on
    wrapper.session.commit()

    return device.serialize


@m.user_endpoint(
    path=["device", "change_name"], requires={"device_uuid": UUID(), "name": Text(min_length=1, max_length=15)}
)
def change_name(data: dict, user: str) -> dict:
    """
    Change the name of the device.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found

    if not device.check_access(user):
        return permission_denied

    name: str = str(data["name"])

    device.name: str = name

    wrapper.session.commit()

    return device.serialize


@m.user_endpoint(path=["device", "delete"], requires={"device_uuid": UUID()})
def delete(data: dict, user: str) -> dict:
    """
    Delete a device.
    :param data: The given data.
    :param user: The user uuid.
    :return: Success or not
    """
    device: Device = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found

    if not device.check_access(user):
        return permission_denied

    wrapper.session.delete(device)
    wrapper.session.commit()

    return success


@m.user_endpoint(path=["device", "spot"], requires={})
def spot(data: dict, user: str) -> dict:
    device: Device = Device.random(user)

    return device.serialize


@m.microservice_endpoint(path=["exist"])
def exist(data: dict, microservice: str) -> dict:
    """
    Does a device exist?
    :param data: The given data.
    :param microservice: The microservice..
    :return: True or False
    """
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    return {"exist": device is not None}


@m.microservice_endpoint(path=["owner"])
def owner(data: dict, microservice: str) -> dict:
    if __name__ == "__main__":
        device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found
    else:
        return {"owner": device.owner}
