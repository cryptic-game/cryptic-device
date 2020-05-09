from typing import List, Optional

from cryptic import register_errors
from sqlalchemy import func

from app import m, wrapper
from models.device import Device
from models.file import File
from models.hardware import Hardware
from models.service import Service
from models.workload import Workload
from resources.errors import device_exists, can_access_device, device_powered_on, is_owner_of_device
from resources.game_content import (
    check_compatible,
    calculate_power,
    create_hardware,
    check_exists,
    delete_items,
    stop_all_service,
    stop_services,
    delete_services,
    delete_files,
)
from schemes import (
    success,
    permission_denied,
    requirement_build,
    requirement_device,
    requirement_change_name,
    already_own_a_device,
    maximum_devices_reached,
    device_not_found,
)
from vars import hardware


@m.user_endpoint(path=["device", "info"], requires=requirement_device)
@register_errors(device_exists)
def device_info(data: dict, user: str, device: Device) -> dict:
    """
    Get public information about a device.
    :param data: The given data.
    :param user: The user uuid.
    :param device: The device.
    :return: The response
    """

    return {
        **device.serialize,
        "hardware": [h.serialize for h in wrapper.session.query(Hardware).filter_by(device_uuid=device.uuid)],
    }


@m.user_endpoint(path=["device", "ping"], requires=requirement_device)
@register_errors(device_exists)
def ping(data: dict, user: str, device: Device) -> dict:
    """
    Ping a device.
    :param data: The given data.
    :param user: The user uuid.
    :param device: The device.
    :return: The response
    """

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

    count: int = wrapper.session.query(func.count(Device.uuid)).filter_by(owner=user).scalar()

    if count >= 3:
        return maximum_devices_reached

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

    m.contact_microservice("service", ["device_init"], {"device_uuid": device.uuid, "user": device.owner})

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

    m.contact_microservice("service", ["device_init"], {"device_uuid": device.uuid, "user": device.owner})

    return device.serialize


@m.user_endpoint(path=["device", "power"], requires=requirement_device)
@register_errors(device_exists, is_owner_of_device)
def power(data: dict, user: str, device: Device) -> dict:
    """
    Turn a device on/off.
    :param data: The given data.
    :param user: The user uuid.
    :param device: The device.
    :return: The response
    """

    device_uuid: str = data["device_uuid"]

    device.powered_on = not device.powered_on
    wrapper.session.commit()

    if not device.powered_on:
        stop_all_service(device_uuid)
        stop_services(device_uuid)
    else:
        m.contact_microservice("service", ["device_restart"], {"device_uuid": device_uuid, "user": device.owner})

    return device.serialize


@m.user_endpoint(path=["device", "change_name"], requires=requirement_change_name)
@register_errors(device_exists, can_access_device, device_powered_on)
def change_name(data: dict, user: str, device: Device) -> dict:
    """
    Change the name of the device.
    :param data: The given data.
    :param user: The user uuid.
    :param device: The device.
    :return: The response
    """

    name: str = str(data["name"])

    device.name = name

    wrapper.session.commit()

    return device.serialize


@m.user_endpoint(path=["device", "delete"], requires=requirement_device)
@register_errors(device_exists)
def delete_device(data: dict, user: str, device: Device) -> dict:
    """
    Delete a device.
    :param data: The given data.
    :param user: The user uuid.
    :param device: The device.
    :return: Success or not
    """

    if device.owner != user:
        return permission_denied

    stop_all_service(device.uuid, delete=True)
    delete_services(device.uuid)  # Removes all Services in MS_Service
    delete_files(device.uuid)  # remove all files

    for hw in wrapper.session.query(Hardware).filter_by(device_uuid=device.uuid):
        m.contact_microservice(
            "inventory",
            ["inventory", "create"],
            {"item_name": hw.hardware_element, "owner": device.owner, "related_ms": "device"},
        )
        wrapper.session.delete(hw)

    device: Device = wrapper.session.query(Device).get(device.uuid)
    wrapper.session.delete(device)
    wrapper.session.commit()

    return success


@m.user_endpoint(path=["device", "spot"], requires={})
def spot(data: dict, user: str) -> dict:
    device: Optional[Device] = Device.random(user)
    if device is None:
        return device_not_found

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


@m.microservice_endpoint(path=["ping"])
@register_errors(device_exists)
def ms_ping(data: dict, microservice: str, device: Device) -> dict:
    return {"online": device.powered_on}


@m.microservice_endpoint(path=["owner"])
@register_errors(device_exists)
def owner(data: dict, microservice: str, device: Device) -> dict:
    return {"owner": device.owner}


@m.microservice_endpoint(path=["delete_user"])
def delete_user(data: dict, microservice: str) -> dict:
    """
    Delete all devices of a user.

    :param data: The given data.
    :param microservice: The microservice.
    :return: Success or not
    """

    user_uuid: str = data["user_uuid"]

    for device in wrapper.session.query(Device).filter_by(owner=user_uuid):

        # delete all files stored on the device
        for file in wrapper.session.query(File).filter_by(device=device.uuid):
            wrapper.session.delete(file)

        # delete all hardware used in the device
        for hardware_element in wrapper.session.query(Hardware).filter_by(device_uuid=device.uuid):
            wrapper.session.delete(hardware_element)

        # delete all workload entries used for the device
        for workload_entry in wrapper.session.query(Workload).filter_by(uuid=device.uuid):
            wrapper.session.delete(workload_entry)

        # delete all services running on the device
        for service in wrapper.session.query(Service).filter_by(device_uuid=device.uuid):
            wrapper.session.delete(service)

        # delete the device itself
        wrapper.session.delete(device)

    wrapper.session.commit()

    return success
