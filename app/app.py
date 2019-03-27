from cryptic import MicroService
from typing import Any, Dict, List
from .objects import Base, engine
from .resources.device import exist as device_exists, handle as device_handle
from .resources.file import handle as file_handle


def handle(endpoint: List[str], data: Dict[str, Any], user: str) -> Dict[str, Any]:
    """
    The main handle function.
    :param endpoint: The given endpoint
    :param data: The given data
    :param user: The given user
    :return: The response
    """
    if endpoint[0] == 'device':
        device_handle(endpoint[1:], data, user)
    elif endpoint[0] == 'file':
        file_handle(endpoint[1:], data, user)
    else:
        return {
            'ok': False,
            'error': 'this endpoint is not supported'
        }


def handle_microservice_requests(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    The main handle function for other microservices.
    :param data: The given data
    :return: The response for the microservice
    """
    if data['endpoint'] == 'exist':
        try:
            device_uuid = data['device_uuid']
        except KeyError:
            return {
                'error': 'no device uuid given'
            }

        return device_exists(device_uuid)

    return {
        'ok': False,
        'error': 'endpoint not supported'
    }


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)

    m: MicroService = MicroService('device', handle, handle_microservice_requests)
    m.run()
