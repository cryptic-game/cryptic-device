from cryptic import MicroService
from typing import Any, Dict, List
from objects import Base, engine


def handle(endpoint: List[str], data: Dict[str, Any], user: str) -> Dict[str, Any]:
    """
    The main handle function.
    :param endpoint: The given endpoint
    :param data: The given data
    :param user: The given user
    :return: The response
    """
    data['user_uuid'] = user
    if endpoint[0] == 'device':
        return handle_device(endpoint[1:], data)
    elif endpoint[0] == 'file':
        return handle_file(endpoint[1:], data)
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

        return exist(device_uuid)

    return {
        'ok': False,
        'error': 'endpoint not supported'
    }


m: MicroService = MicroService('device', handle, handle_microservice_requests)


if __name__ == '__main__':
    from resources.device import handle_device, exist
    from resources.file import handle_file

    Base.metadata.create_all(bind=engine)
    m.run()
