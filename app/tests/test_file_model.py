from unittest import TestCase

from mock.mock_loader import mock
from models.file import File


class TestFileModel(TestCase):
    def setUp(self):
        mock.reset_mocks()

    def test__model__file__structure(self):
        self.assertEqual("device_file", File.__tablename__)
        self.assertTrue(issubclass(File, mock.wrapper.Base))
        for col in ["uuid", "device", "filename", "content", "is_directory", "parent_dir_uuid"]:
            self.assertIn(col, dir(File))

    def test__model__file__serialize(self):
        file = File(
            uuid="file identifier",
            device="the device",
            filename="some_file.txt",
            content="hello world",
            parent_dir_uuid="some_other_identifier",
            is_directory=False,
            is_changeable=False,
        )

        expected_result = {
            "uuid": "file identifier",
            "device": "the device",
            "filename": "some_file.txt",
            "content": "hello world",
            "parent_dir_uuid": "some_other_identifier",
            "is_directory": False,
            "is_changeable": False,
        }
        serialized = file.serialize

        self.assertEqual(expected_result, serialized)

        serialized["content"] = "hi!"
        self.assertEqual(expected_result, file.serialize)

    def test__model__file__create(self):
        actual_result = File.create("my-device", "foo.bar", "super", "baz", False)

        self.assertEqual("my-device", actual_result.device)
        self.assertEqual("foo.bar", actual_result.filename)
        self.assertEqual("baz", actual_result.parent_dir_uuid)
        self.assertEqual(False, actual_result.is_directory)
        self.assertRegex(actual_result.uuid, r"[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}")
        mock.wrapper.session.add.assert_called_with(actual_result)
        mock.wrapper.session.commit.assert_called_with()

    def test__model__device__create__different_uuid(self):
        first_element = File.create("device", "foo.bar", "super", "baz", False).uuid
        second_element = File.create("device", "foo.bar", "super", "baz", False).uuid
        self.assertNotEqual(first_element, second_element)
