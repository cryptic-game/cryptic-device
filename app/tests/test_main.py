from importlib import machinery, util
from unittest import TestCase

from mock.mock_loader import mock
from resources import device, file, hardware
from resources.errors import device_exists, can_access_device, device_powered_on
from schemes import (
    requirement_device,
    requirement_build,
    requirement_change_name,
    requirement_file,
    requirement_file_move,
    requirement_file_update,
    requirement_file_create,
    requirement_service,
)


def import_app(name: str = "app"):
    return machinery.SourceFileLoader(name, util.find_spec("app").origin).load_module()


def import_main(name: str = "main"):
    return machinery.SourceFileLoader(name, util.find_spec("main").origin).load_module()


class TestApp(TestCase):
    def setUp(self):
        mock.reset_mocks()

    def test__microservice_setup(self):
        app = import_app()

        mock.MicroService.assert_called_with("device")
        self.assertEqual(mock.MicroService(), app.m)

        mock.m.get_wrapper.assert_called_with()
        self.assertEqual(mock.m.get_wrapper(), app.wrapper)

    def test__microservice_setup_called(self):
        main = import_main()
        self.assertEqual(import_app(), main.app)

    def test__run_as_main(self):
        import_main("__main__")

        mock.wrapper.Base.metadata.create_all.assert_called_with(bind=mock.wrapper.engine)
        mock.m.run.assert_called_with()

    def test__import_as_module(self):
        import_main()

        mock.wrapper.Base.metadata.create_all.assert_not_called()
        mock.m.run.assert_not_called()

    def test__endpoints_available(self):
        main = import_main("__main__")
        elements = [getattr(main, element_name) for element_name in dir(main)]

        registered_user_endpoints = mock.user_endpoints.copy()
        registered_ms_endpoints = mock.ms_endpoints.copy()

        file_errors = (device_exists, can_access_device, device_powered_on)
        expected_user_endpoints = [
            (["device", "info"], requirement_device, device.device_info, device_exists),
            (["device", "ping"], requirement_device, device.ping, device_exists),
            (["device", "all"], {}, device.list_devices),
            (["device", "create"], requirement_build, device.create_device),
            (["device", "starter_device"], {}, device.starter_device),
            (["device", "power"], requirement_device, device.power, device_exists, can_access_device),
            (["device", "change_name"], requirement_change_name, device.change_name, *file_errors),
            (["device", "delete"], requirement_device, device.delete_device, device_exists),
            (["device", "spot"], {}, device.spot),
            (["file", "all"], requirement_device, file.list_files, *file_errors),
            (["file", "info"], requirement_file, file.file_info, *file_errors),
            (["file", "move"], requirement_file_move, file.move, *file_errors),
            (["file", "update"], requirement_file_update, file.update, *file_errors),
            (["file", "delete"], requirement_file, file.delete_file, *file_errors),
            (["file", "create"], requirement_file_create, file.create_file, *file_errors),
            (["hardware", "build"], requirement_build, hardware.build),
            (["hardware", "resources"], requirement_device, hardware.hardware_resources),
            (["hardware", "process"], requirement_service, hardware.hardware_process),
            (["hardware", "list"], {}, hardware.hardware_list),
        ]

        expected_ms_endpoints = [
            (["exist"], device.exist),
            (["ping"], device.ms_ping, device_exists),
            (["owner"], device.owner, device_exists),
            (["hardware", "register"], hardware.hardware_register),
            (["hardware", "stop"], hardware.hardware_stop),
            (["hardware", "scale"], hardware.hardware_scale),
            (["delete_user"], device.delete_user),
        ]

        for path, requires, func, *errors in expected_user_endpoints:
            self.assertIn((path, requires), registered_user_endpoints)
            endpoint_handler = mock.user_endpoint_handlers[tuple(path)]
            registered_user_endpoints.remove((path, requires))
            self.assertIn(endpoint_handler, elements)
            self.assertEqual(func, endpoint_handler)
            if errors:
                self.assertEqual(tuple(errors), endpoint_handler.__errors__)
            else:
                self.assertNotIn("__errors__", dir(endpoint_handler))

        for path, func, *errors in expected_ms_endpoints:
            self.assertIn(path, registered_ms_endpoints)
            endpoint_handler = mock.ms_endpoint_handlers[tuple(path)]
            registered_ms_endpoints.remove(path)
            self.assertIn(endpoint_handler, elements)
            self.assertEqual(func, endpoint_handler)
            if errors:
                self.assertEqual(tuple(errors), endpoint_handler.__errors__)
            else:
                self.assertNotIn("__errors__", dir(endpoint_handler))

        self.assertFalse(registered_user_endpoints)
        self.assertFalse(registered_ms_endpoints)
