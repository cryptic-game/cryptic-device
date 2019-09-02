from unittest import TestCase

from mock.mock_loader import mock
from models.workload import Workload


class TestWorkloadModel(TestCase):
    def setUp(self):
        mock.reset_mocks()

    def test__model__workload__structure(self):
        self.assertEqual("device_workload", Workload.__tablename__)
        self.assertTrue(issubclass(Workload, mock.wrapper.Base))

        expected_columns = [
            "uuid",
            "performance_cpu",
            "performance_ram",
            "performance_gpu",
            "performance_disk",
            "performance_network",
            "usage_cpu",
            "usage_ram",
            "usage_gpu",
            "usage_disk",
            "usage_network",
        ]
        for col in expected_columns:
            self.assertIn(col, dir(Workload))

    def test__model__workload__serialize(self):
        workload = Workload(
            uuid="device-uuid",
            performance_cpu=2.1,
            performance_ram=2.2,
            performance_gpu=2.3,
            performance_disk=2.4,
            performance_network=2.5,
            usage_cpu=1.1,
            usage_ram=1.2,
            usage_gpu=1.3,
            usage_disk=1.4,
            usage_network=1.5,
        )

        expected_result = {
            "uuid": "device-uuid",
            "performance_cpu": 2.1,
            "performance_ram": 2.2,
            "performance_gpu": 2.3,
            "performance_disk": 2.4,
            "performance_network": 2.5,
            "usage_cpu": 1.1,
            "usage_ram": 1.2,
            "usage_gpu": 1.3,
            "usage_disk": 1.4,
            "usage_network": 1.5,
        }
        serialized = workload.serialize

        self.assertEqual(expected_result, serialized)

        serialized["usage_cpu"] = 13.37
        self.assertEqual(expected_result, workload.serialize)

    def test__model__workload__create(self):
        actual_result = Workload.create("the-device", (3.1, 3.2, 3.3, 3.4, 3.5))

        self.assertEqual("the-device", actual_result.uuid)
        self.assertEqual(3.1, actual_result.performance_cpu)
        self.assertEqual(3.2, actual_result.performance_ram)
        self.assertEqual(3.3, actual_result.performance_gpu)
        self.assertEqual(3.4, actual_result.performance_disk)
        self.assertEqual(3.5, actual_result.performance_network)
        self.assertEqual(0, actual_result.usage_cpu)
        self.assertEqual(0, actual_result.usage_ram)
        self.assertEqual(0, actual_result.usage_gpu)
        self.assertEqual(0, actual_result.usage_disk)
        self.assertEqual(0, actual_result.usage_network)
        mock.wrapper.session.add.assert_called_with(actual_result)
        mock.wrapper.session.commit.assert_called_with()

    def test__model__workload__service(self):
        workload = Workload.create("the-device", (3.1, 3.2, 3.3, 3.4, 3.5))
        workload.service((1.01, 1.02, 1.03, 1.04, 1.05))

        self.assertEqual(1.01, workload.usage_cpu)
        self.assertEqual(1.02, workload.usage_ram)
        self.assertEqual(1.03, workload.usage_gpu)
        self.assertEqual(1.04, workload.usage_disk)
        self.assertEqual(1.05, workload.usage_network)
        mock.wrapper.session.commit.assert_called_with()

    def test__model__workload__display(self):
        workload = Workload.create("the-device", (3.1, 3.2, 3.3, 3.4, 3.5))
        workload.usage_cpu = 1.4
        workload.usage_ram = 3
        workload.usage_disk = 1000
        workload.usage_network = 2.7

        expected_result = {
            "data": {"cpu": 1.4 / 3.1, "ram": 3 / 3.2, "gpu": 0.0, "disk": 1, "network": 2.7 / 3.5},
            "origin": "cryptic-device-display",
            "notify-id": "resource-usage",
        }
        actual_result = workload.display()

        self.assertEqual(expected_result, actual_result)
