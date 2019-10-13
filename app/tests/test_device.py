from unittest import TestCase
from unittest.mock import patch

from mock.mock_loader import mock
from models.device import Device
from models.file import File
from models.hardware import Hardware
from models.service import Service
from models.workload import Workload
from resources import device
from schemes import device_not_found, permission_denied, success, already_own_a_device
from vars import hardware


class TestDevice(TestCase):
    def setUp(self):
        mock.reset_mocks()

        self.query_device = mock.MagicMock()
        self.query_hardware = mock.MagicMock()
        self.query_file = mock.MagicMock()
        self.query_workload = mock.MagicMock()
        self.query_service = mock.MagicMock()
        device.func = self.sqlalchemy_func = mock.MagicMock()
        self.query_func_count = mock.MagicMock()
        mock.wrapper.session.query.side_effect = {
            Device: self.query_device,
            Hardware: self.query_hardware,
            File: self.query_file,
            Workload: self.query_workload,
            Service: self.query_service,
            self.sqlalchemy_func.count(): self.query_func_count,
        }.__getitem__

    def test__user_endpoint__device_info__device_not_found(self):
        self.query_device.get.return_value = None

        expected_result = device_not_found
        actual_result = device.device_info({"device_uuid": "does-not-exist"}, "")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("does-not-exist")

    def test__user_endpoint__device_info__successful(self):
        hardware = [mock.MagicMock() for _ in range(5)]
        mock_device = mock.MagicMock()
        mock_device.serialize = {"foo": "bar", "foo2": "bar2"}

        self.query_device.get.return_value = mock_device
        self.query_hardware.filter_by.return_value = hardware

        expected_result = {"foo": "bar", "foo2": "bar2", "hardware": [e.serialize for e in hardware]}
        actual_result = device.device_info({"device_uuid": mock_device.uuid}, "")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with(mock_device.uuid)
        self.query_hardware.filter_by.assert_called_with(device_uuid=mock_device.uuid)

    def test__user_endpoint__device_ping__device_not_found(self):
        self.query_device.get.return_value = None

        expected_result = device_not_found
        actual_result = device.ping({"device_uuid": "my-device"}, "")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my-device")

    def test__user_endpoint__device_ping_successful(self):
        mock_device = mock.MagicMock()
        self.query_device.get.return_value = mock_device

        expected_result = {"online": mock_device.powered_on}
        actual_result = device.ping({"device_uuid": "my-device"}, "")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my-device")

    def test__user_endpoint__device_all(self):
        devices = [mock.MagicMock() for _ in range(5)]
        self.query_device.filter_by().all.return_value = devices

        expected_result = {"devices": [d.serialize for d in devices]}
        actual_result = device.list_devices({}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.filter_by.assert_called_with(owner="user")

    @patch("resources.device.check_compatible")
    def test__user_endpoint__device_create__not_compatible(self, compatible_patch):
        compatible_patch.return_value = False, {"error": "some error message"}
        data = mock.MagicMock()

        expected_result = {"error": "some error message"}
        actual_result = device.create_device(data, "user")

        self.assertEqual(expected_result, actual_result)
        compatible_patch.assert_called_with(data)

    @patch("resources.device.check_exists")
    @patch("resources.device.check_compatible")
    def test__user_endpoint__device_create__inventory_incomplete(self, compatible_patch, exists_patch):
        compatible_patch.return_value = True, {}
        exists_patch.return_value = False, {"error": "some other error message"}
        data = mock.MagicMock()

        expected_result = {"error": "some other error message"}
        actual_result = device.create_device(data, "user")

        self.assertEqual(expected_result, actual_result)
        compatible_patch.assert_called_with(data)
        exists_patch.assert_called_with("user", data)

    @patch("resources.device.File")
    @patch("resources.device.delete_items")
    @patch("resources.device.create_hardware")
    @patch("resources.device.calculate_power")
    @patch("resources.device.Workload")
    @patch("resources.device.Device")
    @patch("resources.device.check_exists")
    @patch("resources.device.check_compatible")
    def test__user_endpoint__device_create__successful(
        self,
        compatible_patch,
        exists_patch,
        device_patch,
        workload_patch,
        calculate_patch,
        create_patch,
        delete_patch,
        file_patch,
    ):
        compatible_patch.return_value = True, {}
        exists_patch.return_value = True, {}
        data = mock.MagicMock()

        mock_device = device_patch.create()

        expected_result = mock_device.serialize
        actual_result = device.create_device(data, "user")

        self.assertEqual(expected_result, actual_result)
        compatible_patch.assert_called_with(data)
        exists_patch.assert_called_with("user", data)
        calculate_patch.assert_called_with(data)
        device_patch.create.assert_called_with("user", True)
        workload_patch.create.assert_called_with(mock_device.uuid, calculate_patch())
        create_patch.assert_called_with(data, mock_device.uuid)
        delete_patch.assert_called_with("user", data)
        file_patch.create.assert_called_with(mock_device.uuid, "/", "", None, True, False)

    def test__user_endpoint__device_starter_device__already_own_a_device(self):
        self.query_func_count.filter_by().scalar.return_value = 1

        expected_result = already_own_a_device
        actual_result = device.starter_device({}, "user")

        self.assertEqual(expected_result, actual_result)
        self.sqlalchemy_func.count.assert_called_with(Device.uuid)
        self.query_func_count.filter_by.assert_called_with(owner="user")

    @patch("resources.device.create_hardware")
    @patch("resources.device.calculate_power")
    @patch("resources.device.Workload")
    @patch("resources.device.Device.create")
    def test__user_endpoint__device_starter_device__successful(
        self, device_create_patch, workload_patch, calculate_patch, create_patch
    ):
        self.query_func_count.filter_by().scalar.return_value = 0

        mock_device = device_create_patch()

        expected_result = mock_device.serialize
        actual_result = device.starter_device({}, "user")

        self.assertEqual(expected_result, actual_result)
        self.sqlalchemy_func.count.assert_called_with(Device.uuid)
        self.query_func_count.filter_by.assert_called_with(owner="user")
        calculate_patch.assert_called_with(hardware["start_pc"])
        device_create_patch.assert_called_with("user", True)
        workload_patch.create.assert_called_with(mock_device.uuid, calculate_patch())
        create_patch.assert_called_with(hardware["start_pc"], mock_device.uuid)

    def test__user_endpoint__device_power__device_not_found(self):
        self.query_device.get.return_value = None

        expected_result = device_not_found
        actual_result = device.power({"device_uuid": "my-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my-device")

    def test__user_endpoint__device_power__permission_denied(self):
        self.query_device.get().check_access.return_value = False

        expected_result = permission_denied
        actual_result = device.power({"device_uuid": "my-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my-device")
        self.query_device.get().check_access.assert_called_with("user")

    def test__user_endpoint__device_power__turn_on(self):
        mock_device = self.query_device.get()
        mock_device.check_access.return_value = True
        mock_device.powered_on = False

        expected_result = mock_device.serialize
        actual_result = device.power({"device_uuid": "my-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my-device")
        self.query_device.get().check_access.assert_called_with("user")
        self.assertTrue(mock_device.powered_on)

    @patch("resources.device.stop_services")
    @patch("resources.device.stop_all_service")
    def test__user_endpoint__device_power__turn_off(self, stop_all_patch, stop_services_patch):
        mock_device = self.query_device.get()
        mock_device.check_access.return_value = True
        mock_device.powered_on = True

        expected_result = mock_device.serialize
        actual_result = device.power({"device_uuid": "my device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my device")
        self.query_device.get().check_access.assert_called_with("user")
        self.assertFalse(mock_device.powered_on)
        stop_all_patch.assert_called_with("my device")
        stop_services_patch.assert_called_with("my device")

    def test__user_endpoint__device_change_name__device_not_found(self):
        self.query_device.get.return_value = None

        expected_result = device_not_found
        actual_result = device.change_name({"device_uuid": "the-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("the-device")

    def test__user_endpoint__device_change_name__permission_denied(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = False
        self.query_device.get.return_value = mock_device

        expected_result = permission_denied
        actual_result = device.change_name({"device_uuid": "the-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("the-device")
        mock_device.check_access.assert_called_with("user")

    def test__user_endpoint__device_change_name__successful(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True
        self.query_device.get.return_value = mock_device

        expected_result = mock_device.serialize
        actual_result = device.change_name({"device_uuid": "the-device", "name": "new-name"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("the-device")
        mock_device.check_access.assert_called_with("user")
        self.assertEqual("new-name", mock_device.name)
        mock.wrapper.session.commit.assert_called_with()

    def test__user_endpoint__device_delete__device_not_found(self):
        self.query_device.get.return_value = None

        expected_result = device_not_found
        actual_result = device.delete_device({"device_uuid": "the-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("the-device")

    def test__user_endpoint__device_delete__permission_denied(self):
        mock_device = mock.MagicMock()
        mock_device.owner = "other-user"
        self.query_device.get.return_value = mock_device

        expected_result = permission_denied
        actual_result = device.delete_device({"device_uuid": "the-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("the-device")

    @patch("resources.device.delete_services")
    @patch("resources.device.stop_all_service")
    def test__user_endpoint__device_delete__successful(self, sas_patch, ds_patch):
        mock_device = mock.MagicMock()
        mock_device.owner = "user"
        self.query_device.get.return_value = mock_device

        expected_result = success
        actual_result = device.delete_device({"device_uuid": "the-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("the-device")
        sas_patch.assert_called_with("the-device", delete=True)
        ds_patch.assert_called_with("the-device")
        mock.wrapper.session.delete.assert_called_with(mock_device)
        mock.wrapper.session.commit.assert_called_with()

    @patch("resources.device.Device")
    def test__user_endpoint__device_spot(self, device_patch):
        expected_result = device_patch.random().serialize
        actual_result = device.spot({}, "user")

        self.assertEqual(expected_result, actual_result)
        device_patch.random.assert_called_with("user")

    def test__ms_endpoint__exist__not_found(self):
        self.query_device.get.return_value = None

        expected_result = {"exist": False}
        actual_result = device.exist({"device_uuid": "my device"}, "")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my device")

    def test__ms_endpoint__exist__exists(self):
        self.query_device.get.return_value = "device"

        expected_result = {"exist": True}
        actual_result = device.exist({"device_uuid": "my device"}, "")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my device")

    def test__ms_endpoint__owner__device_not_found(self):
        self.query_device.get.return_value = None

        expected_result = device_not_found
        actual_result = device.owner({"device_uuid": "my device"}, "")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my device")

    def test__ms_endpoint__owner__successful(self):
        mock_device = mock.MagicMock()
        self.query_device.get.return_value = mock_device

        expected_result = {"owner": mock_device.owner}
        actual_result = device.owner({"device_uuid": "my device"}, "")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my device")

    def test__ms_endpoint__delete_user(self):
        devices = [mock.MagicMock() for _ in range(5)]
        files = {}
        hardware_elements = {}
        workloads = {}
        services = {}
        to_delete = devices.copy()
        for i in range(5):
            uuid = devices[i].uuid
            files[uuid] = [mock.MagicMock() for _ in range(5)]
            hardware_elements[uuid] = [mock.MagicMock() for _ in range(5)]
            workloads[uuid] = [mock.MagicMock() for _ in range(5)]
            services[uuid] = [mock.MagicMock() for _ in range(5)]
            to_delete += files[uuid] + hardware_elements[uuid] + workloads[uuid] + services[uuid]

        self.query_device.filter_by.return_value = devices.copy()
        mock.wrapper.session.delete.side_effect = to_delete.remove
        self.query_file.filter_by.side_effect = lambda device: files[device]
        self.query_hardware.filter_by.side_effect = lambda device_uuid: hardware_elements[device_uuid]
        self.query_workload.filter_by.side_effect = lambda uuid: workloads[uuid]
        self.query_service.filter_by.side_effect = lambda device_uuid: services[device_uuid]

        self.assertEqual(success, device.delete_user({"user_uuid": "the-user"}, "server"))
        self.assertFalse(to_delete)
        self.query_device.filter_by.assert_called_with(owner="the-user")
        mock.wrapper.session.commit.assert_called_with()
