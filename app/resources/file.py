from typing import List, Dict, Any, Optional
from models.file import File
from objects import session
from models.device import Device
from models.file import CONTENT_LENGTH


# ENDPOINTS FOR HANDLE #

def get_all(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get all files of a device.
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = Device.query.filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(data):
        return {
            'ok': False,
            'error': 'no access to the file in this device'
        }

    return {
        'files': File.query.filter_by(device=device.uuid).first()
    }


def info(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get information about a file
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = Device.query.filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(data):
        return {
            'ok': False,
            'error': 'no access to the file in this device'
        }

    file: Optional[File] = File.query.filter_by(uuid=data['file_uuid']).first()

    if file is None:
        return {
            'ok': False,
            'error': 'invalid file uuid'
        }

    return file.serialize


def update(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a file.
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = Device.query.filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(data):
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

    file: Optional[File] = File.query.filter_by(uuid=data['device_uuid']).first()

    if file is None:
        return {
            'ok': False,
            'error': 'invalid file uuid'
        }

    file_count: int = session.query(File).filter(
        File.device == device.uuid).filter(File.filename == filename).first()[0]

    if file.filename != filename and file_count > 0:
        return {
            'ok': False,
            'error': 'filename already taken'
        }

    if len(content) > CONTENT_LENGTH:
        return {
            'ok': False,
            'error': 'content is too big'
        }

    file.filename: str = filename
    file.content: str = content

    session.commit()

    return file.serialize


def delete(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a file.
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = Device.query.filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(data):
        return {
            'ok': False,
            'error': 'no access to the file in this device'
        }

    file: Optional[File] = File.query.filter_by(uuid=data['file_uuid']).first()

    if file is None:
        return {
            'ok': False,
            'error': 'invalid file uuid'
        }

    session.delete(file)
    session.commit()

    return {'ok': True}


def create(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new file.
    :param data: The given data
    :return: The response
    """
    device: Optional[Device] = Device.query.filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(data):
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

    file_count: int = session.query(File).filter(
        File.device == device.uuid).filter(File.filename == filename).first()[0]

    if file_count != 0:
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


# HANDLE FUNCTION #

def file_handle(endpoint: List[str], data: Dict[str, Any], user: str) -> Dict[str, Any]:
    """
    Handle function for microservice.
    :param endpoint: The list of the endpoint elements
    :param data: The data given for this function
    :param user: The user's uuid
    :return: The response

    Endpoints:

    /<string:device>        # Endpoint that doesn't require a file uuid
        /<string:uuid>      # Endpoint that requires uuid
            /info           # Get information about a file
            /update         # Update a file
            /delete         # Delete a file
        /all                # Get all files of a device
        /remove             # Create a new file

    Data:

    filename: str               # The filename for creating and updating a file
    content: str                # The content for creating and updating a file
    device_uuid: str            # The device-uuid -> endpoint[0]
    file_uuid: Optional[str]    # The file-uuid -> endpoint[1]
    """
    data['user_uuid']: str = user
    data['device_uuid']: str = endpoint[0]

    if len(endpoint) == 3:
        data['file_uuid']: str = endpoint[1]
        if endpoint[2] == 'info':  # Get information about a file
            return info(data)

        elif endpoint[2] == 'update':  # Update a file
            return update(data)

        elif endpoint[2] == 'remove':  # Delete a file
            return delete(data)

    elif len(endpoint) == 2:
        if endpoint[1] == 'all':  # Get all files of a device
            return get_all(data)

        elif endpoint[1] == 'create':  # Create a new file
            return create(data)

    return {
        'ok': False,
        'error': 'endpoint not supported'
    }
