from unittest import TestCase
from unittest.mock import patch

from mock.mock_loader import mock
from models.device import Device


class TestDeviceModel(TestCase):
    def setUp(self):
        mock.reset_mocks()

        self.query_device = mock.MagicMock()
        mock.wrapper.session.query.side_effect = {Device: self.query_device}.__getitem__

    def test__model__device__structure(self):
        self.assertEqual("device_device", Device.__tablename__)
        self.assertTrue(issubclass(Device, mock.wrapper.Base))
        for col in ["uuid", "name", "owner", "powered_on"]:
            self.assertIn(col, dir(Device))

    def test__model__device__serialize(self):
        device = Device(uuid="unique device identifier", name="a nice device", owner="the owner", powered_on=True)

        expected_result = {
            "uuid": "unique device identifier",
            "name": "a nice device",
            "owner": "the owner",
            "powered_on": True,
        }
        serialized = device.serialize

        self.assertEqual(expected_result, serialized)

        serialized["name"] = "other name"
        self.assertEqual(expected_result, device.serialize)

    def test__model__device__create(self):
        actual_result = Device.create("the user", False)

        self.assertEqual("the user", actual_result.owner)
        self.assertEqual(False, actual_result.powered_on)
        self.assertRegex(actual_result.uuid, r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}")
        self.assertRegex(actual_result.name, r"[a-zA-Z0-9]{1,15}")
        mock.wrapper.session.add.assert_called_with(actual_result)
        mock.wrapper.session.commit.assert_called_with()

    def test__model__device__create__different_uuid(self):
        first_element = Device.create("user", True).uuid
        second_element = Device.create("user", True).uuid
        self.assertNotEqual(first_element, second_element)

    def test__model__device__check_access__device_owner(self):
        device = Device.create("the-user", True)

        actual_result = device.check_access("the-user")

        self.assertEqual(True, actual_result)
        mock.m.contact_microservice.assert_not_called()

    def test__model__device__check_access__part_owner(self):
        device = Device.create("the-user", True)

        expected_result = mock.m.contact_microservice()["ok"]
        actual_result = device.check_access("other-user")

        self.assertEqual(expected_result, actual_result)
        mock.m.contact_microservice.assert_called_with(
            "service", ["check_part_owner"], {"user_uuid": "other-user", "device_uuid": device.uuid}
        )

    @patch("models.device.and_")
    @patch("models.device.Device.powered_on")
    @patch("models.device.Device.owner")
    @patch("models.device.func.random")
    def test__model__device__random__multiple_devices(self, random_patch, owner_patch, power_patch, and_patch):
        self.query_device.filter().order_by().first.return_value = "random device"
        owner_patch.__ne__.return_value = "owner-ne"

        expected_result = "random device"
        actual_result = Device.random("some user")

        self.assertEqual(expected_result, actual_result)
        owner_patch.__ne__.assert_called_with("some user")
        and_patch.assert_called_with("owner-ne", power_patch)
        random_patch.assert_called_with()
        self.query_device.filter.assert_called_with(and_patch())
        self.query_device.filter().order_by.assert_called_with(random_patch())
