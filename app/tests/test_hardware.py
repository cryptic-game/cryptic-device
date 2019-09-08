from unittest import TestCase
from unittest.mock import patch

from mock.mock_loader import mock
from models.service import Service
from models.workload import Workload

from resources import hardware
from schemes import device_not_found, service_already_running, service_not_running, success, service_not_found


class TestHardware(TestCase):
    def setUp(self):
        mock.reset_mocks()

        self.query_service = mock.MagicMock()
        self.query_workload = mock.MagicMock()
        mock.wrapper.session.query.side_effect = {
            Service: self.query_service,
            Workload: self.query_workload,
        }.__getitem__

    @patch("resources.hardware.check_compatible")
    def test__user_endpoint__hardware_build__not_compatible(self, check_compatible_patch):
        check_compatible_patch.return_value = False, {"error": "error_message"}
        data = mock.MagicMock()

        expected_result = {"error": "error_message"}
        actual_result = hardware.build(data, "user")

        self.assertEqual(expected_result, actual_result)
        check_compatible_patch.assert_called_with(data)

    @patch("resources.hardware.calculate_power")
    @patch("resources.hardware.check_compatible")
    def test__user_endpoint__hardware_build__successful(self, check_compatible_patch, calculate_power_patch):
        check_compatible_patch.return_value = True, {}
        data = mock.MagicMock()

        expected_result = {"success": True, "performance": calculate_power_patch()}
        actual_result = hardware.build(data, "user")

        self.assertEqual(expected_result, actual_result)
        check_compatible_patch.assert_called_with(data)
        calculate_power_patch.assert_called_with(data)

    def test__user_endpoint__hardware_resources__device_not_found(self):
        self.query_workload.get.return_value = None

        expected_result = device_not_found
        actual_result = hardware.hardware_resources({"device_uuid": "some-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_workload.get.assert_called_with("some-device")

    def test__user_endpoint__hardware_resources__successful(self):
        mock_workload = mock.MagicMock()
        self.query_workload.get.return_value = mock_workload

        expected_result = mock_workload.display()
        actual_result = hardware.hardware_resources({"device_uuid": "some-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_workload.get.assert_called_with("some-device")
        mock_workload.display.assert_called()

    def test__ms_endpoint__hardware_register__device_not_found(self):
        self.query_workload.get.return_value = None

        expected_result = device_not_found
        actual_result = hardware.hardware_register({"device_uuid": "the-device"}, "ms")

        self.assertEqual(expected_result, actual_result)
        self.query_workload.get.assert_called_with("the-device")

    def test__ms_endpoint__hardware_register__service_already_running(self):
        mock_workload = mock.MagicMock()
        self.query_workload.get.return_value = mock_workload
        self.query_service.get.return_value = mock.MagicMock()

        expected_result = service_already_running
        actual_result = hardware.hardware_register({"device_uuid": "the-device", "service_uuid": "my-service"}, "ms")

        self.assertEqual(expected_result, actual_result)
        self.query_workload.get.assert_called_with("the-device")
        self.query_service.get.assert_called_with("my-service")

    @patch("resources.hardware.Service.create")
    @patch("resources.hardware.scale_resources")
    @patch("resources.hardware.generate_scale")
    @patch("resources.hardware.dict2tuple")
    def test__ms_endpoint__hardware_register__successful(
        self, dict_patch, generate_scale_patch, scale_patch, service_create_patch
    ):
        mock_workload = mock.MagicMock()
        other_services = [mock.MagicMock() for _ in range(5)]
        self.query_workload.get.return_value = mock_workload
        self.query_service.get.return_value = None
        self.query_service.filter_by().all.return_value = other_services
        dict_patch.return_value = 1, 2, 3, 4, 5
        scales = generate_scale_patch.return_value = 2, 3, 5, 7, 11

        ser = mock.MagicMock()
        ser.allocated_cpu = 21
        ser.allocated_ram = 13
        ser.allocated_gpu = 8
        ser.allocated_disk = 5
        ser.allocated_network = 3
        service_create_patch.return_value = ser

        data = {"device_uuid": "the-device", "service_uuid": "my-service", "user": "user"}

        expected_result = {
            "service_uuid": ser.service_uuid,
            "cpu": ser.allocated_cpu * scales[0],
            "ram": ser.allocated_ram * scales[1],
            "gpu": ser.allocated_gpu * scales[2],
            "disk": ser.allocated_disk * scales[3],
            "network": ser.allocated_network * scales[4],
        }
        actual_result = hardware.hardware_register(data, "ms")

        self.assertEqual(expected_result, actual_result)
        self.query_service.filter_by.assert_called_with(device_uuid="the-device")
        dict_patch.assert_called_with(data)
        generate_scale_patch.assert_called_with(dict_patch(), mock_workload)
        scale_patch.assert_called_with(other_services, generate_scale_patch())
        mock_workload.service.assert_called_with(dict_patch())
        service_create_patch.assert_called_with("the-device", "my-service", dict_patch())
        mock_workload.workload_notification.assert_called_with("device-hardware-register")
        mock.m.contact_user.assert_called_with("user", mock_workload.workload_notification())

    def test__ms_endpoint__hardware_stop__service_not_running(self):
        self.query_service.get.return_value = None
        data = {"device_uuid": "the-device", "service_uuid": "my-service", "user": "user"}

        expected_result = service_not_running
        actual_result = hardware.hardware_stop(data, "ms")

        self.assertEqual(expected_result, actual_result)
        self.query_service.get.assert_called_with("my-service")

    def test__ms_endpoint__hardware_stop__device_not_found(self):
        mock_service = mock.MagicMock()
        self.query_service.get.return_value = mock_service
        self.query_workload.get.return_value = None

        data = {"device_uuid": "the-device", "service_uuid": "my-service", "user": "user"}

        expected_result = device_not_found
        actual_result = hardware.hardware_stop(data, "ms")

        self.assertEqual(expected_result, actual_result)
        self.query_service.get.assert_called_with("my-service")
        self.query_workload.get.assert_called_with("the-device")

    @patch("resources.hardware.scale_resources")
    @patch("resources.hardware.generate_scale")
    @patch("resources.hardware.turn")
    def test__ms_endpoint__hardware_stop__successful(self, turn_patch, generate_patch, scale_patch):
        mock_service = mock.MagicMock()
        mock_workload = mock.MagicMock()
        other_services = [mock.MagicMock() for _ in range(5)]
        self.query_service.get.return_value = mock_service
        self.query_workload.get.return_value = mock_workload
        self.query_service.filter_by().all.return_value = other_services

        data = {"device_uuid": "the-device", "service_uuid": "my-service", "user": "user"}

        expected_result = success
        actual_result = hardware.hardware_stop(data, "ms")

        self.assertEqual(expected_result, actual_result)
        self.query_service.get.assert_called_with("my-service")
        self.query_workload.get.assert_called_with("the-device")
        mock_service.export.assert_called_with()
        turn_patch.assert_called_with(mock_service.export())
        mock.wrapper.session.delete.assert_called_with(mock_service)
        mock.wrapper.session.commit.assert_called_with()
        mock_workload.service.assert_called_with(turn_patch())
        generate_patch.assert_called_with(turn_patch(), mock_workload)
        self.query_service.filter_by.assert_called_with(device_uuid="the-device")
        scale_patch.assert_called_with(other_services, generate_patch())
        mock_workload.workload_notification.assert_called_with("device_hardware_stop")
        mock.m.contact_user.assert_called_with("user", mock_workload.workload_notification())

    def test__ms_endpoint__hardware_scale__service_not_found(self):
        data = {"device_uuid": "the-device", "service_uuid": "my-service", "user": "user"}
        self.query_service.get.return_value = None

        expected_result = service_not_found
        actual_result = hardware.hardware_scale(data, "ms")

        self.assertEqual(expected_result, actual_result)
        self.query_service.get.assert_called_with("my-service")

    @patch("resources.hardware.scale_resources")
    @patch("resources.hardware.generate_scale")
    @patch("resources.hardware.dict2tuple")
    @patch("resources.hardware.turn")
    def test__ms_endpoint__hardware_scale__successful(self, turn_patch, dict_patch, generate_patch, scale_patch):
        data = {"device_uuid": "the-device", "service_uuid": "my-service", "user": "user"}

        mock_service = mock.MagicMock()
        mock_service.allocated_cpu = 21
        mock_service.allocated_ram = 13
        mock_service.allocated_gpu = 8
        mock_service.allocated_disk = 5
        mock_service.allocated_network = 3

        mock_workload = mock.MagicMock()
        other_services = [mock.MagicMock() for _ in range(5)]
        self.query_service.get.return_value = mock_service
        self.query_workload.get.return_value = mock_workload
        self.query_service.filter_by().all.return_value = other_services
        scales = generate_patch.return_value = 2, 3, 5, 7, 11

        expected_calls = [turn_patch(), dict_patch()]
        mock_workload.service.side_effect = lambda a: self.assertEqual(expected_calls.pop(0), a)

        expected_result = {
            "service_uuid": mock_service.service_uuid,
            "cpu": mock_service.allocated_cpu * scales[0],
            "ram": mock_service.allocated_ram * scales[1],
            "gpu": mock_service.allocated_gpu * scales[2],
            "disk": mock_service.allocated_disk * scales[3],
            "network": mock_service.allocated_network * scales[4],
        }
        actual_result = hardware.hardware_scale(data, "ms")

        self.assertEqual(expected_result, actual_result)
        self.query_service.get.assert_called_with("my-service")
        self.query_workload.get.assert_called_with("the-device")
        self.query_service.filter_by.assert_called_with(device_uuid="the-device")
        mock_service.export.assert_called_with()
        turn_patch.assert_called_with(mock_service.export())
        dict_patch.assert_called_with(data)
        generate_patch.assert_called_with(dict_patch(), mock_workload)
        mock_service.overwrite.assert_called_with(dict_patch())
        scale_patch.assert_called_with(other_services, generate_patch())
        mock_workload.workload_notification.assert_called_with("device_hardware_scale")
        mock.m.contact_user.assert_called_with("user", mock_workload.workload_notification())
