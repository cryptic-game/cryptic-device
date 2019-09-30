from typing import List, Optional

from sqlalchemy import func

from app import m, wrapper
from models.device import Device
from models.hardware import Hardware
from models.workload import Workload
from models.file import File
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
from schemes import (
    success,
    device_not_found,
    permission_denied,
    requirement_build,
    requirement_device,
    requirement_change_name,
    already_own_a_device,
)
from vars import hardware


@m.user_endpoint(path=["device", "info"], requires=requirement_device)
def device_info(data: dict, user: str) -> dict:
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


@m.user_endpoint(path=["device", "ping"], requires=requirement_device)
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
def list_devices(data: dict, user: str) -> dict:
    """
    Get all devices
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    devices: List[Device] = wrapper.session.query(Device).filter_by(owner=user).all()

    return {"devices": [d.serialize for d in devices]}


@m.user_endpoint(path=["device", "create"], requires=requirement_build)
def create_device(data: dict, user: str) -> dict:
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

    count: int = wrapper.session.query(func.count(Device.uuid)).filter_by(owner=user).scalar()

    if count > 0:
        return already_own_a_device

    performance: tuple = calculate_power(hardware["start_pc"])

    device: Device = Device.create(user, True)

    Workload.create(device.uuid, performance)

    create_hardware(hardware["start_pc"], device.uuid)

    return device.serialize


@m.user_endpoint(path=["device", "power"], requires=requirement_device)
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


@m.user_endpoint(path=["device", "change_name"], requires=requirement_change_name)
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


@m.user_endpoint(path=["device", "delete"], requires=requirement_device)
def delete_device(data: dict, user: str) -> dict:
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


@m.microservice_endpoint(path=["delete_user"])
def delete_user(data: dict) -> dict:
    """
    Delete all devices of a user.
    :param data: The given data.
    :return: Success or not
    """

    user_uuid = data.get("user_uuid")

    devices: list = wrapper.session.query(Device).filter_by(owner=user_uuid).all()

    if devices is not None:
        for device in devices:

            # delete all files stored on the device
            files: list = wrapper.session.query(File).filter_by(device=device.uuid).all()
            for file in files:
                wrapper.session.delete(file)

            # delete all hardware used in the device
            hardware_list: list = wrapper.session.query(Hardware).filter_by(device_uuid=device.uuid).all()
            for hardware_element in hardware_list:
                wrapper.session.delete(hardware_element)

            # delete the device itself
            wrapper.session.delete(device)

        wrapper.session.commit()

    return success