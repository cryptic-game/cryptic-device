from typing import Optional
from scheme import UUID, Text
from app import m, wrapper
from models.device import Device
from models.file import CONTENT_LENGTH
from models.file import File
from schemes import file_already_exists, file_not_found, device_not_found, permission_denied, success


@m.user_endpoint(path=["file", "all"], requires={"device_uuid": UUID()})
def get_all(data: dict, user: str) -> dict:
    """
    Get all files of a device.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found

    if not device.check_access(user):
        return permission_denied

    return {"files": [f.serialize for f in wrapper.session.query(File).filter_by(device=device.uuid).all()]}


@m.user_endpoint(path=["file", "info"], requires={"device_uuid": UUID(), "file_uuid": UUID()})
def info(data: dict, user: str) -> dict:
    """
    Get information about a file
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found

    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).get(data["file_uuid"])

    if file is None:
        return file_not_found

    return file.serialize


@m.user_endpoint(
    path=["file", "move"],
    requires={"device_uuid": UUID(), "file_uuid": UUID(), "filename": Text(min_length=1, max_length=64)},
)
def move(data: dict, user: str) -> dict:
    device_uuid: str = data["device_uuid"]
    file_uuid = data["file_uuid"]
    filename = data["filename"]

    device: Optional[Device] = wrapper.session.query(Device).get(device_uuid)

    if device is None:
        return device_not_found
    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).filter_by(device=device_uuid, uuid=file_uuid).first()

    if file is None:
        return file_not_found

    if wrapper.session.query(File).filter_by(device=device_uuid, filename=filename).first() is not None:
        return file_already_exists

    file.filename: str = filename
    wrapper.session.commit()

    return file.serialize


@m.user_endpoint(
    path=["file", "update"],
    requires={"device_uuid": UUID(), "file_uuid": UUID(), "content": Text(max_length=CONTENT_LENGTH)},
)
def update(data: dict, user: str) -> dict:
    """
    Update the content of a file.

    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """

    device_uuid: str = data["device_uuid"]
    file_uuid = data["file_uuid"]
    content = data["content"]

    device: Optional[Device] = wrapper.session.query(Device).get(device_uuid)

    if device is None:
        return device_not_found
    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).filter_by(device=device_uuid, uuid=file_uuid).first()

    if file is None:
        return file_not_found

    file.content: str = content
    wrapper.session.commit()

    return file.serialize


@m.user_endpoint(path=["file", "delete"], requires={"device_uuid": UUID(), "file_uuid": UUID()})
def delete(data: dict, user: str) -> dict:
    """
    Delete a file.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found

    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).get(data["file_uuid"])

    if file is None:
        return file_not_found

    wrapper.session.delete(file)
    wrapper.session.commit()

    return success


@m.user_endpoint(
    path=["file", "create"],
    requires={
        "device_uuid": UUID(),
        "filename": Text(min_length=1, max_length=64),
        "content": Text(max_length=CONTENT_LENGTH),
    },
)
def create(data: dict, user: str) -> dict:
    """
    Create a new file.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found

    if not device.check_access(user):
        return permission_denied

    filename: str = data["filename"]
    content: str = data["content"]

    file_count: int = wrapper.session.query(File).filter_by(device=device.uuid, filename=filename).count()

    if file_count > 0:
        return file_already_exists

    file: Optional[File] = File.create(device.uuid, filename, content)

    return file.serialize
