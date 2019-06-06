from typing import Optional
from scheme import *
from app import m, wrapper
from models.device import Device
from models.file import CONTENT_LENGTH
from models.file import File


@m.user_endpoint(path=["file", "all"])
def get_all(data: dict, user: str) -> dict:
    """
    Get all files of a device.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return invalid_device

    if not device.check_access(user):
        return permission_denied

    return {
        'files': [f.serialize for f in wrapper.session.query(File).filter_by(device=device.uuid).all()]
    }


@m.user_endpoint(path=["file", "info"])
def info(data: dict, user: str) -> dict:
    """
    Get information about a file
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return invalid_device

    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).filter_by(uuid=data['file_uuid']).first()

    if file is None:
        return invalid_file

    return file.serialize


@m.user_endpoint(path=["file", "update"])
def update(data: dict, user: str) -> dict:
    """
    Update a file.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return invalid_device

    if not device.check_access(user):
        return permission_denied

    if "filename" not in data:
        return no_file_name
    if "content" not in data:
        return no_content

    file: Optional[File] = wrapper.session.query(File).filter_by(uuid=data['file_uuid']).first()

    if file is None:
        return invalid_file

    file_count: int = wrapper.session.query(File).filter_by(device=device.uuid, filename=data["filename"]).count()

    if file.filename != data["filename"] and file_count > 0:
        return no_file

    if len(data["content"]) > CONTENT_LENGTH:
        return length_exceeded

    file.filename: str = data["filename"]
    file.content: str = data["content"]

    wrapper.session.commit()

    return file.serialize


@m.user_endpoint(path=["file", "delete"])
def delete(data: dict, user: str) -> dict:
    """
    Delete a file.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return invalid_device

    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).filter_by(uuid=data['file_uuid']).first()

    if file is None:
        return invalid_file

    wrapper.session.delete(file)
    wrapper.session.commit()

    return success


@m.user_endpoint(path=["file", "create"])
def create(data: dict, user: str) -> dict:
    """
    Create a new file.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return invalid_device

    if not device.check_access(user):
        return permission_denied
    if 'filename' in data:
        filename: str = data['filename']
    else:
        return no_file_name
    if 'content' in data:
        content: str = data['content']
    else:
        return no_content

    file_count: int = wrapper.session.query(File).filter_by(device=device.uuid, filename=filename).count()

    if file_count > 0:
        return file_already_exists

    if len(filename) == 0:
        return empty_name_not_allowed

    if len(filename) > 64:
        return name_too_long

    if len(content) > CONTENT_LENGTH:
        return length_exceeded

    file: Optional[File] = File.create(device.uuid, filename, content)

    return file.serialize
