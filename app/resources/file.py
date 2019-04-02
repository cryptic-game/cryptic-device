from typing import List, Dict, Any, Optional
from models.file import File
from objects import session
from models.device import Device
from models.file import CONTENT_LENGTH
from app import m


# ENDPOINTS FOR HANDLE #

@m.user_endpoint(path=["file", "all"])
def get_all(data: dict, user: str) -> dict:
    """
    Get all files of a device.
    :param user:
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {'ok': False, 'error': 'invalid device uuid'}

    if not device.check_access(user):
        return {'ok': False, 'error': 'no access to the file in this device'}

    return {
        'files': [f.serialize for f in session.query(File).filter_by(device=device.uuid).all()]
    }


@m.user_endpoint(path=["file", "info"])
def info(data: dict, user: str) -> dict:
    """
    Get information about a file
    :param user:
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {'ok': False, 'error': 'invalid device uuid'}

    if not device.check_access(user):
        return {'ok': False, 'error': 'no access to the file in this device'}

    file: Optional[File] = session.query(File).filter_by(uuid=data['file_uuid']).first()

    if file is None:
        return {
            'ok': False,
            'error': 'invalid file uuid'
        }

    return file.serialize


@m.user_endpoint(path=["file", "update"])
def update(data: dict, user: str) -> dict:
    """
    Update a file.
    :param user:
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(user):
        return {'ok': False, 'error': 'no access to the file in this device'}

    if "filename" not in data:
        return {'ok': False, 'error': 'no filename given'}
    if "content" not in data:
        return {'ok': False, 'error': 'no content given'}

    file: Optional[File] = session.query(File).filter_by(uuid=data['file_uuid']).first()

    if file is None:
        return {
            'ok': False,
            'error': 'invalid file uuid'
        }

    file_count: int = len(session.query(File).filter_by(device=device.uuid).filter_by(filename=data["filename"]).all())

    if file.filename != data["filename"] and file_count > 0:
        return {'ok': False, 'error': 'no file with this name exist'}

    if len(data["content"]) > CONTENT_LENGTH:
        return {
            'ok': False,
            'error': 'content is too big'
        }

    file.filename: str = data["filename"]
    file.content: str = data["content"]

    session.commit()

    return file.serialize


@m.user_endpoint(path=["file", "delete"])
def delete(data: dict, user: str) -> dict:
    """
    Delete a file.
    :param user:
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(user):
        return {
            'ok': False,
            'error': 'no access to the file in this device'
        }

    file: Optional[File] = session.query(File).filter_by(uuid=data['file_uuid']).first()

    if file is None:
        return {
            'ok': False,
            'error': 'invalid file uuid'
        }

    session.delete(file)
    session.commit()

    return {'ok': True}


@m.user_endpoint(path=["file", "create"])
def create(data: dict, user: str) -> dict:
    """
    Create a new file.
    :param user:
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = session.query(Device).filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(user):
        return {
            'ok': False,
            'error': 'no access to the file in this device'
        }

    try:
        filename: str = data['filename']
    except KeyError:
        return {
            'ok': False,
            'error': 'no filename given'
        }
    try:
        content: str = data['content']
    except KeyError:
        return {
            'ok': False,
            'error': 'no content given'
        }

    file_count: int = len(session.query(File).filter_by(device=device.uuid).filter_by(filename=filename).all())

    if file_count > 0:
        return {
            'ok': False,
            'error': 'filename already taken'
        }

    if len(content) > CONTENT_LENGTH:
        return {
            'ok': False,
            'error': 'content is too big'
        }

    file: Optional[File] = File.create(device.uuid, filename, content)

    return file.serialize
