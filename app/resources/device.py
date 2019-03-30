from typing import List, Optional, Dict, Any
from objects import session
from models.device import Device
from sqlalchemy import func

# ENDPOINTS FOR HANDLE #

def public_info(device_uuid: str) -> Dict[str, Any]:
    """
    Get public information about a device.
    :param device_uuid: The uuid of the device
    :return: The response
    """
    device: Optional[Device] = Device.query.filter_by(uuid=device_uuid).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    return device.serialize


def private_info(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get private information about a device.
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
            'error': 'no access to this device'
        }

    return device.serialize


def ping(device_uuid: str) -> Dict[str, Any]:
    """
    Ping a device.
    :param device_uuid: The given device uuid
    :return: The response
    """
    device: Optional[Device] = Device.query.filter_by(uuid=device_uuid).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    return {
        "online": device.powered_on
    }


def get_all(user_uuid: str) -> Dict[str, Any]:
    """
    Get all devices
    :param user_uuid: The given user uuid
    :return: The response
    """
    devices: List[Device] = Device.query.filter_by(owner=user_uuid).all()

    return {
        "devices": [d.serialize for d in devices]
    }


def create(user_uuid: str) -> Dict[str, Any]:
    """
    Create a device.
    :param user_uuid: The given user uuid
    :return: The response
    """
    device_count = session.query(Device).filter(Device.owner == user_uuid).first()

    if device_count:
        return {
            'ok': False,
            'error': 'you already own a device'
        }

    device: Device = Device.create(user_uuid, 1, True)

    return device.serialize


def power(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Turn a device on/off.
    :param data: The given data
    :return: The response
    """
    device: Device = Device.query.filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(data):
        return {
            'ok': False,
            'error': 'no access to this device'
        }

    device.powered_on: bool = not device.powered_on
    session.commit()

    return device.serialize


def change_name(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Change the name of the device.
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
            'error': 'no access to this device'
        }

    try:
        name: str = str(data['name'])
    except KeyError:
        return {
            'ok': False,
            'error': 'no name given'
        }

    device.name: str = name

    session.commit()

    return device.serialize


def delete(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a device.
    :param data: The given data
    :return: The response
    """
    device: Device = Device.query.filter_by(uuid=data['device_uuid']).first()

    if device is None:
        return {
            'ok': False,
            'error': 'invalid device uuid'
        }

    if not device.check_access(data):
        return {
            'ok': False,
            'error': 'no access to this device'
        }

    session.delete(device)
    session.commit()

    return {"ok": True}


# HANDLE MICROSERVICE REQUESTS #

def exist(device_uuid: str) -> Dict[str, Any]:
    """
    Does a device exist?
    :param device_uuid: The device uuid
    :return: True or False
    """
    device: Optional[Device] = Device.query.filter_by(uuid=device_uuid).first()

    return {
        'exists': device is not None
    }


# HANDLE FUNCTION #

def handle_device(endpoint: List[str], data: Dict[str, Any], user: str) -> Dict[str, Any]:
    """
    Handle function for microservice.
    :param endpoint: The list of the endpoint elements
    :param data: The data given for this function
    :param user: The user's uuid
    :return: The response

    Endpoints:

    /public               # The endpoint every user has access to
        /<string:uuid>    # The device's uuid
            /info         # Get information about a device -> device.serialize
            /ping         # Ping a device -> device.powered_on
    /private              # The endpoint only the owner has access to
        /<string:uuid>    # The device's uuid
            /info         # Get private information about the device -> device.serialize
            /power        # Turn the device on/off
            /name          # Change the name of the device
            /remove       # Delete a device
        /all              # Get a list of all devices
        /create           # Create a device

    Data:

    name                            # For /private/<string:uuid>/put to change the device's name
    device_uuid: Optional[str}      # The device-uuid -> endpoint[1]
    user_uuid: str                  # The user's uuid
    """
    data['user_uuid']: str = user

    if endpoint[0] == 'public':
        data['device_uuid']: str = endpoint[1]

        if endpoint[2] == 'info':  # Get public information about a device
            return public_info(data['device_uuid'])

        elif endpoint[2] == 'ping':  # Ping a device
            return ping(data['device_uuid'])

    elif endpoint[0] == 'private':
        if endpoint[1] == 'all':  # Get all devices
            return get_all(user)

        elif endpoint[1] == 'create':  # Create a device
            return create(user)

        else:
            data['device_uuid']: str = endpoint[1]
            if endpoint[2] == 'info':  # Get private information about the device
                return private_info(data)

            elif endpoint[2] == 'power':  # Turn the device on/off
                return power(data)

            elif endpoint[2] == 'name':  # Change the name of the device
                return change_name(data)

            elif endpoint[2] == 'remove':  # Delete a device
                return delete(data)

    return {
        'ok': False,
        'error': 'endpoint not supported'
    }
