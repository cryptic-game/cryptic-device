from typing import Optional

from sqlalchemy import func

from app import m, wrapper
from cryptic import register_errors
from models.device import Device
from models.file import File
from resources.errors import device_exists, can_access_device, device_powered_on
from schemes import (
    file_already_exists,
    file_not_found,
    success,
    requirement_device,
    requirement_file,
    requirement_file_move,
    requirement_file_update,
    requirement_file_create,
)


@m.user_endpoint(path=["file", "all"], requires=requirement_device)
@register_errors(device_exists, can_access_device, device_powered_on)
def list_files(data: dict, user: str, device: Device) -> dict:
    """
    Get all files of a device.
    :param data: The given data.
    :param user: The user uuid.
    :param device: The device of the file.
    :return: The response
    """

    return {"files": [f.serialize for f in wrapper.session.query(File).filter_by(device=device.uuid).all()]}


@m.user_endpoint(path=["file", "info"], requires=requirement_file)
@register_errors(device_exists, can_access_device, device_powered_on)
def file_info(data: dict, user: str, device: Device) -> dict:
    """
    Get information about a file
    :param data: The given data.
    :param user: The user uuid.
    :param device: The device of the file.
    :return: The response
    """

    file: Optional[File] = wrapper.session.query(File).filter_by(device=device.uuid, uuid=(data["file_uuid"])).first()

    if file is None:
        return file_not_found

    return file.serialize


@m.user_endpoint(path=["file", "move"], requires=requirement_file_move)
@register_errors(device_exists, can_access_device, device_powered_on)
def move(data: dict, user: str, device: Device) -> dict:
    file_uuid = data["file_uuid"]
    filename = data["filename"]

    file: Optional[File] = wrapper.session.query(File).filter_by(device=device.uuid, uuid=file_uuid).first()

    if file is None:
        return file_not_found

    if wrapper.session.query(File).filter_by(device=device.uuid, filename=filename).first() is not None:
        return file_already_exists

    file.filename = filename
    wrapper.session.commit()

    return file.serialize


@m.user_endpoint(path=["file", "update"], requires=requirement_file_update)
@register_errors(device_exists, can_access_device, device_powered_on)
def update(data: dict, user: str, device: Device) -> dict:
    """
    Update the content of a file.

    :param data: The given data.
    :param user: The user uuid.
    :param device: The device of the file.
    :return: The response
    """

    file: Optional[File] = wrapper.session.query(File).filter_by(device=device.uuid, uuid=(data["file_uuid"])).first()

    if file is None:
        return file_not_found

    file.content = data["content"]
    wrapper.session.commit()

    return file.serialize


@m.user_endpoint(path=["file", "delete"], requires=requirement_file)
@register_errors(device_exists, can_access_device, device_powered_on)
def delete_file(data: dict, user: str, device: Device) -> dict:
    """
    Delete a file.
    :param data: The given data.
    :param user: The user uuid.
    :param device: The device of the file.
    :return: The response
    """

    file: Optional[File] = wrapper.session.query(File).filter_by(device=device.uuid, uuid=(data["file_uuid"])).first()

    if file is None:
        return file_not_found

    wrapper.session.delete(file)
    wrapper.session.commit()

    return success


@m.user_endpoint(path=["file", "create"], requires=requirement_file_create)
@register_errors(device_exists, can_access_device, device_powered_on)
def create_file(data: dict, user: str, device: Device) -> dict:
    """
    Create a new file.
    :param data: The given data.
    :param user: The user uuid.
    :param device: The device of the file.
    :return: The response
    """

    filename: str = data["filename"]
    content: str = data["content"]

    file_count: int = wrapper.session.query(func.count(File.uuid)).filter_by(
        device=device.uuid, filename=filename
    ).scalar()

    if file_count > 0:
        return file_already_exists

    file: File = File.create(device.uuid, filename, content)

    return file.serialize
