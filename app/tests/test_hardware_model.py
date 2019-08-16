from unittest import TestCase

from mock.mock_loader import mock
from models.hardware import Hardware


class TestHardwareModel(TestCase):
    def setUp(self):
        mock.reset_mocks()

    def test__model__hardware__structure(self):
        self.assertEqual("device_hardware", Hardware.__tablename__)
        self.assertTrue(issubclass(Hardware, mock.wrapper.Base))
        for col in ["uuid", "device_uuid", "hardware_element", "hardware_type"]:
            self.assertIn(col, dir(Hardware))

    def test__model__hardware__serialize(self):
        hardware = Hardware(
            uuid="some-uuid", device_uuid="the-device", hardware_element="Crossfire ZX1000", hardware_type="ram"
        )

        expected_result = {
            "uuid": "some-uuid",
            "device_uuid": "the-device",
            "hardware_element": "Crossfire ZX1000",
            "hardware_type": "ram",
        }
        serialized = hardware.serialize

        self.assertEqual(expected_result, serialized)

        serialized["hardware_type"] = "gpu"
        self.assertEqual(expected_result, hardware.serialize)

    def test__model__hardware__create(self):
        actual_result = Hardware.create("my-device", "Zero MX One", "mainboard")

        self.assertEqual("my-device", actual_result.device_uuid)
        self.assertEqual("Zero MX One", actual_result.hardware_element)
        self.assertEqual("mainboard", actual_result.hardware_type)
        self.assertRegex(actual_result.uuid, r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}")
        mock.wrapper.session.add.assert_called_with(actual_result)
        mock.wrapper.session.commit.assert_called_with()

    def test__model__hardware__create__different_uuid(self):
        first_element = Hardware.create("my-device", "Zero MX One", "mainboard").uuid
        second_element = Hardware.create("my-device", "Zero MX One", "mainboard").uuid
        self.assertNotEqual(first_element, second_element)
