from typing import Optional

from scheme import UUID, Text

from app import m, wrapper
from models.device import Device
from models.file import CONTENT_LENGTH
from models.file import File
from schemes import *


@m.user_endpoint(path=["file", "all"], requires={
    "device_uuid": UUID()
})
def get_all(data: dict, user: str) -> dict:
    """
    Get all files of a device.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return invalid_device_uuid

    if not device.check_access(user):
        return permission_denied

    return {
        'files': [f.serialize for f in wrapper.session.query(File).filter_by(device=device.uuid).all()]
    }


@m.user_endpoint(path=["file", "info"], requires={
    "device_uuid": UUID(),
    "file_uuid": UUID()
})
def info(data: dict, user: str) -> dict:
    """
    Get information about a file
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return invalid_device_uuid

    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).filter_by(uuid=data['file_uuid']).first()

    if file is None:
        return invalid_file_uuid

    return file.serialize


@m.user_endpoint(path=["file", "update"], requires={
    "device_uuid": UUID(),
    "file_uuid": UUID(),
    "filename": Text(min_length=1, max_length=64),
    "content": Text(max_length=CONTENT_LENGTH)
})
def update(data: dict, user: str) -> dict:
    """
    Update a file.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return invalid_device_uuid

    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).filter_by(uuid=data['file_uuid']).first()

    if file is None:
        return invalid_file_uuid

    file_count: int = wrapper.session.query(File).filter_by(device=device.uuid, filename=data["filename"]).count()

    if file.filename != data["filename"] and file_count > 0:
        return file_not_found

    file.filename: str = data["filename"]
    file.content: str = data["content"]

    wrapper.session.commit()

    return file.serialize


@m.user_endpoint(path=["file", "delete"], requires={
    "device_uuid": UUID(),
    "file_uuid": UUID()
})
def delete(data: dict, user: str) -> dict:
    """
    Delete a file.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return invalid_device_uuid

    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).filter_by(uuid=data['file_uuid']).first()

    if file is None:
        return invalid_file_uuid

    wrapper.session.delete(file)
    wrapper.session.commit()

    return success


@m.user_endpoint(path=["file", "create"], requires={
    "device_uuid": UUID(),
    "filename": Text(min_length=1, max_length=64),
    "content": Text(max_length=CONTENT_LENGTH)
})
def create(data: dict, user: str) -> dict:
    """
    Create a new file.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return invalid_device_uuid

    if not device.check_access(user):
        return permission_denied

    filename: str = data['filename']
    content: str = data['content']

    file_count: int = wrapper.session.query(File).filter_by(device=device.uuid, filename=filename).count()

    if file_count > 0:
        return file_already_exists

    file: Optional[File] = File.create(device.uuid, filename, content)

    return file.serialize
