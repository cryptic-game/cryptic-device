from unittest import TestCase
from unittest.mock import patch

from mock.mock_loader import mock
from models.device import Device
from models.file import File
from resources import file
from schemes import file_not_found, file_already_exists, success


class TestFile(TestCase):
    def setUp(self):
        mock.reset_mocks()

        self.query_device = mock.MagicMock()
        self.query_file = mock.MagicMock()
        file.func = self.sqlalchemy_func = mock.MagicMock()
        self.query_func_count = mock.MagicMock()
        mock.wrapper.session.query.side_effect = {
            Device: self.query_device,
            File: self.query_file,
            self.sqlalchemy_func.count(): self.query_func_count,
        }.__getitem__

    def test__user_endpoint__file_all(self):
        mock_device = mock.MagicMock()
        files = [mock.MagicMock() for _ in range(5)]

        self.query_file.filter_by().all.return_value = files

        expected_result = {"files": [f.serialize for f in files]}
        actual_result = file.list_files({"device_uuid": mock_device.uuid}, "user", mock_device)

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid)

    def test__user_endpoint__file_info__file_not_found(self):
        mock_device = mock.MagicMock()

        self.query_file.filter_by().first.return_value = None

        expected_result = file_not_found
        actual_result = file.file_info({"device_uuid": mock_device.uuid, "file_uuid": "myfile"}, "user", mock_device)

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid="myfile")

    def test__user_endpoint__file_info__successful(self):
        mock_device = mock.MagicMock()
        mock_file = mock.MagicMock()

        self.query_file.filter_by().first.return_value = mock_file

        expected_result = mock_file.serialize
        actual_result = file.file_info(
            {"device_uuid": mock_device.uuid, "file_uuid": mock_file.uuid}, "user", mock_device
        )

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid=mock_file.uuid)

    def test__user_endpoint__file_move__file_not_found(self):
        mock_device = mock.MagicMock()

        self.query_file.filter_by().first.return_value = None

        expected_result = file_not_found
        actual_result = file.move(
            {"device_uuid": mock_device.uuid, "file_uuid": "my-file", "filename": "new-name"}, "user", mock_device
        )

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid="my-file")

    def test__user_endpoint__file_move__file_already_exists(self):
        mock_device = mock.MagicMock()
        mock_file = mock.MagicMock()

        def handle_file_query(**kwargs):
            out = mock.MagicMock()
            if "filename" in kwargs:
                self.assertEqual({"device": mock_device.uuid, "filename": "new-name"}, kwargs)
                out.first.return_value = mock.MagicMock()
            else:
                self.assertEqual({"device": mock_device.uuid, "uuid": "my-file"}, kwargs)
                out.first.return_value = mock_file
            return out

        self.query_file.filter_by.side_effect = handle_file_query

        expected_result = file_already_exists
        actual_result = file.move(
            {"device_uuid": mock_device.uuid, "file_uuid": "my-file", "filename": "new-name"}, "user", mock_device
        )

        self.assertEqual(expected_result, actual_result)

    def test__user_endpoint__file_move__successful(self):
        mock_device = mock.MagicMock()
        mock_file = mock.MagicMock()

        def handle_file_query(**kwargs):
            out = mock.MagicMock()
            if "filename" in kwargs:
                self.assertEqual({"device": mock_device.uuid, "filename": "new-name"}, kwargs)
                out.first.return_value = None
            else:
                self.assertEqual({"device": mock_device.uuid, "uuid": "my-file"}, kwargs)
                out.first.return_value = mock_file
            return out

        self.query_file.filter_by.side_effect = handle_file_query

        expected_result = mock_file.serialize
        actual_result = file.move(
            {"device_uuid": mock_device.uuid, "file_uuid": "my-file", "filename": "new-name"}, "user", mock_device
        )

        self.assertEqual(expected_result, actual_result)
        self.assertEqual("new-name", mock_file.filename)
        mock.wrapper.session.commit.assert_called_with()

    def test__user_endpoint__file_update__file_not_found(self):
        mock_device = mock.MagicMock()

        self.query_file.filter_by().first.return_value = None

        expected_result = file_not_found
        actual_result = file.update(
            {"device_uuid": mock_device.uuid, "file_uuid": "my-file", "content": "test"}, "user", mock_device
        )

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid="my-file")

    def test__user_endpoint__file_update__successful(self):
        mock_device = mock.MagicMock()
        mock_file = mock.MagicMock()

        self.query_file.filter_by().first.return_value = mock_file

        expected_result = mock_file.serialize
        actual_result = file.update(
            {"device_uuid": mock_device.uuid, "file_uuid": mock_file.uuid, "content": "test"}, "user", mock_device
        )

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid=mock_file.uuid)
        self.assertEqual("test", mock_file.content)
        mock.wrapper.session.commit.assert_called_with()

    def test__user_endpoint__file_delete__file_not_found(self):
        mock_device = mock.MagicMock()

        self.query_file.filter_by().first.return_value = None

        expected_result = file_not_found
        actual_result = file.delete_file({"device_uuid": mock_device.uuid, "file_uuid": "my-file"}, "user", mock_device)

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid="my-file")

    def test__user_endpoint__file_delete__successful(self):
        mock_device = mock.MagicMock()
        mock_file = mock.MagicMock()

        self.query_file.filter_by().first.return_value = mock_file

        expected_result = success
        actual_result = file.delete_file(
            {"device_uuid": mock_device.uuid, "file_uuid": mock_file.uuid}, "user", mock_device
        )

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid=mock_file.uuid)
        mock.wrapper.session.delete.assert_called_with(mock_file)
        mock.wrapper.session.commit.assert_called_with()

    def test__user_endpoint__file_create__file_already_exists(self):
        mock_device = mock.MagicMock()

        self.query_func_count.filter_by().scalar.return_value = 1

        expected_result = file_already_exists
        actual_result = file.create_file(
            {"device_uuid": mock_device.uuid, "filename": "test-file", "content": "some random content here"},
            "user",
            mock_device,
        )

        self.assertEqual(expected_result, actual_result)
        self.sqlalchemy_func.count.assert_called_with(File.uuid)
        self.query_func_count.filter_by.assert_called_with(device=mock_device.uuid, filename="test-file")

    @patch("resources.file.File.create")
    def test__user_endpoint__file_create__successful(self, file_create_patch):
        mock_device = mock.MagicMock()

        self.query_func_count.filter_by().scalar.return_value = 0

        expected_result = file_create_patch().serialize
        actual_result = file.create_file(
            {"device_uuid": mock_device.uuid, "filename": "testfile", "content": "some random content here"},
            "user",
            mock_device,
        )

        self.assertEqual(expected_result, actual_result)
        self.sqlalchemy_func.count.assert_called_with(File.uuid)
        self.query_func_count.filter_by.assert_called_with(device=mock_device.uuid, filename="testfile")
        file_create_patch.assert_called_with(mock_device.uuid, "testfile", "some random content here")
