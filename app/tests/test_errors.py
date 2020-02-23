from unittest import TestCase

from mock.mock_loader import mock
from models.device import Device
from models.file import File
from resources import errors
from resources.errors import MicroserviceException
from schemes import device_not_found, permission_denied, device_powered_off, file_not_found


class TestErrors(TestCase):
    def setUp(self):
        mock.reset_mocks()

        self.query_device = mock.MagicMock()
        self.query_file = mock.MagicMock()
        mock.wrapper.session.query.side_effect = {Device: self.query_device, File: self.query_file}.__getitem__

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

    def test__file_exists__device_not_found(self):
        self.query_file.filter_by().first.return_value = None
        mock_device = mock.MagicMock()

        with self.assertRaises(MicroserviceException) as context:
            errors.file_exists({"file_uuid": "my-file"}, "", mock_device)

        self.assertEqual(file_not_found, context.exception.error)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid="my-file")

    def test__file_exists__successful(self):
        mock_file = self.query_file.filter_by().first.return_value = mock.MagicMock()
        mock_device = mock.MagicMock()

        self.assertEqual((mock_device, mock_file), errors.file_exists({"file_uuid": "my-file"}, "", mock_device))
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid="my-file")
