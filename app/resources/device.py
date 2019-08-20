from typing import List, Optional

from scheme import UUID, Text, Union
from sqlalchemy import func

from app import m, wrapper
from models.device import Device
from models.hardware import Hardware
from models.workload import Workload
from resources.game_content import (
    check_compatible,
    calculate_power,
    create_hardware,
    check_exists,
    delete_items,
    stop_all_service,
    stop_services,
    delete_services,
)
from schemes import success, device_not_found, permission_denied, requirement_build, already_own_a_device
from vars import hardware


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

    return {
        **device.serialize,
        "hardware": [
            hardware.serialize for hardware in wrapper.session.query(Hardware).filter_by(device_uuid=device.uuid)
        ],
    }


@m.user_endpoint(path=["device", "ping"], requires={"device_uuid": UUID()})
def ping(data: dict, user: str) -> dict:
    """
    Ping a device.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

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

    delete_items(user, data)

    return device.serialize


@m.user_endpoint(path=["device", "starter_device"], requires={})
def starter_device(data: dict, user: str) -> dict:
    """
    Creates a device for starters
    :param data: The given data
    :param user: The user uuid.
    :return: the response
    """

    count: int = wrapper.session.query(Device).filter_by(owner=user).count()

    if count > 0:
        return already_own_a_device

    performance: tuple = calculate_power(hardware["start_pc"])

    device: Device = Device.create(user, True)

    Workload.create(device.uuid, performance)

    create_hardware(hardware["start_pc"], device.uuid)

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

    device.powered_on = not device.powered_on
    wrapper.session.commit()

    if not device.powered_on:
        stop_all_service(data["device_uuid"])
        stop_services(data["device_uuid"])

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

    device.name = name

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

    stop_all_service(data["device_uuid"], delete=True)
    delete_services(data["device_uuid"])  # Removes all Services in MS_Service

    device: Device = wrapper.session.query(Device).get(data["device_uuid"])
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
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found
    else:
        return {"owner": device.owner}
