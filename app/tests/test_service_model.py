from unittest import TestCase

from mock.mock_loader import mock
from models.service import Service


class TestServiceModel(TestCase):
    def setUp(self):
        mock.reset_mocks()

    def test__model__service__structure(self):
        self.assertEqual("device_service_req", Service.__tablename__)
        self.assertTrue(issubclass(Service, mock.wrapper.Base))

        expected_columns = [
            "service_uuid",
            "device_uuid",
            "allocated_cpu",
            "allocated_ram",
            "allocated_gpu",
            "allocated_disk",
            "allocated_network",
        ]
        for col in expected_columns:
            self.assertIn(col, dir(Service))

    def test__model__service__serialize(self):
        service = Service(
            service_uuid="the-service",
            device_uuid="my-device",
            allocated_cpu=2.0,
            allocated_ram=3.0,
            allocated_gpu=5.0,
            allocated_disk=7.0,
            allocated_network=11.0,
        )

        expected_result = {
            "service_uuid": "the-service",
            "device_uuid": "my-device",
            "allocated_cpu": 2.0,
            "allocated_ram": 3.0,
            "allocated_gpu": 5.0,
            "allocated_disk": 7.0,
            "allocated_network": 11.0,
        }
        serialized = service.serialize

        self.assertEqual(expected_result, serialized)

        serialized["allocated_ram"] = 42
        self.assertEqual(expected_result, service.serialize)

    def test__model__service__create(self):
        actual_result = Service.create("my-device", "some-service", (1.1, 2.1, 3.2, 4.3, 5.5))

        self.assertEqual("my-device", actual_result.device_uuid)
        self.assertEqual("some-service", actual_result.service_uuid)
        self.assertEqual(1.1, actual_result.allocated_cpu)
        self.assertEqual(2.1, actual_result.allocated_ram)
        self.assertEqual(3.2, actual_result.allocated_gpu)
        self.assertEqual(4.3, actual_result.allocated_disk)
        self.assertEqual(5.5, actual_result.allocated_network)
        mock.wrapper.session.add.assert_called_with(actual_result)
        mock.wrapper.session.commit.assert_called_with()

    def test__model__service__export(self):
        service = Service.create("my-device", "some-service", (1.1, 2.1, 3.2, 4.3, 5.5))

        expected_result = (1.1, 2.1, 3.2, 4.3, 5.5)
        actual_result = service.export()

        self.assertEqual(expected_result, actual_result)

    def test__model__service__overwrite(self):
        service = Service.create("my-device", "some-service", (1.1, 2.1, 3.2, 4.3, 5.5))
        service.overwrite((0.1, 0.2, 0.3, 0.4, 0.5))

        self.assertEqual(0.1, service.allocated_cpu)
        self.assertEqual(0.2, service.allocated_ram)
        self.assertEqual(0.3, service.allocated_gpu)
        self.assertEqual(0.4, service.allocated_disk)
        self.assertEqual(0.5, service.allocated_network)
