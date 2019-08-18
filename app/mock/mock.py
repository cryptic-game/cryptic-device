from unittest.mock import MagicMock

MicroService = MagicMock()
Config = MagicMock()
DatabaseWrapper = MagicMock()
get_config = MagicMock()

m = MicroService()

user_endpoints = []
user_endpoint_handlers = {}
ms_endpoints = []
ms_endpoint_handlers = {}


def user_endpoint_decorator(path, requires):
    def decorator(f):
        user_endpoints.append((path, requires))
        user_endpoint_handlers[tuple(path)] = f
        return f

    return decorator


def ms_endpoint_decorator(path):
    def decorator(f):
        ms_endpoints.append(path)
        ms_endpoint_handlers[tuple(path)] = f
        return f

    return decorator


m.user_endpoint = MagicMock(side_effect=user_endpoint_decorator)
m.microservice_endpoint = MagicMock(side_effect=ms_endpoint_decorator)

wrapper = m.get_wrapper()


class Base:
    metadata = MagicMock()

    def __init__(self, **kwargs):
        self._sa_instance_state = "useless"
        for key, value in kwargs.items():
            setattr(self, key, value)


wrapper.Base = Base


def reset_mocks():
    MicroService.reset_mock()
    Config.reset_mock()
    DatabaseWrapper.reset_mock()
    get_config.reset_mock()

    wrapper.Base.metadata.reset_mock()
    m.contact_microservice.side_effect = None
    wrapper.session.delete.side_effect = None
