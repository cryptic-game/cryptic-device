from unittest import TestCase

from mock.mock_loader import mock
from models.device import Device
from resources import errors
from resources.errors import MicroserviceException
from schemes import device_not_found, permission_denied, device_powered_off


class TestErrors(TestCase):
    def setUp(self):
        mock.reset_mocks()

        self.query_device = mock.MagicMock()
        mock.wrapper.session.query.side_effect = {Device: self.query_device}.__getitem__

    def test__register_errors__without_exception(self):
        e = [mock.MagicMock() for _ in range(3)]
        deco = errors.register_errors(*e)
        f = mock.MagicMock()
        inner = deco(f)
        args = ({"data": None}, "user")

        expected_result = f()
        actual_result = inner(*args)

        self.assertEqual(expected_result, actual_result)
        e[0].assert_called_with(*args)
        e[1].assert_called_with(*args, e[0]())
        e[2].assert_called_with(*args, e[1]())
        f.assert_called_with(*args, e[2]())

    def test__register_errors__with_exception(self):
        def raise_error(*_):
            raise MicroserviceException({"error": True})

        e = [raise_error]
        deco = errors.register_errors(*e)
        f = mock.MagicMock()
        inner = deco(f)
        args = ({"data": None}, "user")

        expected_result = {"error": True}
        actual_result = inner(*args)

        self.assertEqual(expected_result, actual_result)

    def test__device_exists__device_not_found(self):
        self.query_device.get.return_value = None

        with self.assertRaises(MicroserviceException) as context:
            errors.device_exists({"device_uuid": "my-device"}, "")

        self.assertEqual(device_not_found, context.exception.error)
        self.query_device.get.assert_called_with("my-device")

    def test__device_exists__successful(self):
        mock_device = self.query_device.get.return_value = mock.MagicMock()

        self.assertEqual(mock_device, errors.device_exists({"device_uuid": "my-device"}, ""))
        self.query_device.get.assert_called_with("my-device")

    def test__can_access_device__permission_denied(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = False

        with self.assertRaises(MicroserviceException) as context:
            errors.can_access_device({}, "user", mock_device)

        self.assertEqual(permission_denied, context.exception.error)
        mock_device.check_access.assert_called_with("user")

    def test__can_access_device__successful(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True

        self.assertEqual(mock_device, errors.can_access_device({}, "user", mock_device))
        mock_device.check_access.assert_called_with("user")

    def test__device_powered_on__device_powered_off(self):
        mock_device = mock.MagicMock()
        mock_device.powered_on = False

        with self.assertRaises(MicroserviceException) as context:
            errors.device_powered_on({}, "", mock_device)

        self.assertEqual(device_powered_off, context.exception.error)

    def test__device_powered_on__device_powered_on(self):
        mock_device = mock.MagicMock()
        mock_device.powered_on = True

        self.assertEqual(mock_device, errors.device_powered_on({}, "", mock_device))
