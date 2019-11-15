from unittest import TestCase
from unittest.mock import patch

from mock.mock_loader import mock
from models.device import Device
from models.file import File
from resources import file
from schemes import (
    device_not_found,
    permission_denied,
    file_not_found,
    file_already_exists,
    success,
    directories_can_not_be_updated,
    file_not_changeable,
    parent_directory_not_found,
    can_not_move_dir_into_itself,
    directory_can_not_have_textcontent,
)


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
        actual_result = file.list_files({"device_uuid": mock_device.uuid, "parent_dir_uuid": "0"}, "user", mock_device)

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, parent_dir_uuid="0")

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
            {
                "device_uuid": mock_device.uuid,
                "file_uuid": "my-file",
                "new_filename": "new-name",
                "new_parent_dir_uuid": "0",
            },
            "user",
            mock_device,
        )

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid="my-file")

    def test__user_endpoint__file_move__file_already_exists(self):
        mock_device = mock.MagicMock()
        mock_file = mock.MagicMock()

        def handle_file_query(**kwargs):
            out = mock.MagicMock()
            if "filename" in kwargs:
                self.assertEqual({"device": mock_device.uuid, "filename": "new-name", "parent_dir_uuid": "0"}, kwargs)
                out.first.return_value = mock.MagicMock()
            else:
                self.assertEqual({"device": mock_device.uuid, "uuid": "my-file"}, kwargs)
                out.first.return_value = mock_file
            return out

        self.query_file.filter_by.side_effect = handle_file_query

        expected_result = file_already_exists
        actual_result = file.move(
            {
                "device_uuid": mock_device.uuid,
                "file_uuid": "my-file",
                "new_filename": "new-name",
                "new_parent_dir_uuid": "0",
            },
            "user",
            mock_device,
        )

        self.assertEqual(expected_result, actual_result)

    def test__user_endpoint__file_move__file_not_changeable(self):
        mock_device = mock.MagicMock()
        mock_file = mock.MagicMock()
        mock_file.is_changeable = False

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

        expected_result = file_not_changeable
        actual_result = file.move(
            {
                "device_uuid": mock_device.uuid,
                "file_uuid": "my-file",
                "new_filename": "new-name",
                "new_parent_dir_uuid": "0",
            },
            "user",
        )

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with(mock_device.uuid)
        mock_device.check_access.assert_called_with("user")

    def test__user_endpoint__file_move__parent_directory_not_found(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True
        mock_file = mock.MagicMock()
        mock_file.is_changeable = True

        self.query_device.get.return_value = mock_device

        def handle_file_query(**kwargs):
            out = mock.MagicMock()
            if "filename" in kwargs:
                self.assertEqual({"device": mock_device.uuid, "filename": "new-name", "parent_dir_uuid": "0"}, kwargs)
                out.first.return_value = None
            elif "uuid" in kwargs and kwargs["uuid"] == "0":
                self.assertEqual({"device": mock_device.uuid, "uuid": "0", "is_directory": True}, kwargs)
                out.first.return_value = None
            else:
                self.assertEqual({"device": mock_device.uuid, "uuid": "my-file"}, kwargs)
                out.first.return_value = mock_file
            return out

        self.query_file.filter_by.side_effect = handle_file_query

        expected_result = parent_directory_not_found
        actual_result = file.move(
            {
                "device_uuid": mock_device.uuid,
                "file_uuid": "my-file",
                "new_filename": "new-name",
                "new_parent_dir_uuid": "0",
            },
            "user",
        )

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with(mock_device.uuid)
        mock_device.check_access.assert_called_with("user")

    def test__user_endpoint__file_move__can_not_move_dir_into_itself(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True
        mock_file = mock.MagicMock()
        mock_file.is_changeable = True
        mock_file.is_directory = True
        mock_file.uuid = "3"
        filesystem = {}
        for i in range(0, 11):
            dir_mock = mock.MagicMock()
            dir_mock.parent_dir_uuid = str(i - 1)
            dir_mock.uuid = str(i)
            filesystem.update({str(i): dir_mock})
        filesystem["0"].parent_dir_uuid = None

        self.query_device.get.return_value = mock_device

        def handle_file_query(**kwargs):
            out = mock.MagicMock()
            if "filename" in kwargs:
                self.assertEqual({"device": mock_device.uuid, "filename": "new-name", "parent_dir_uuid": "10"}, kwargs)
                out.first.return_value = None
            elif "uuid" in kwargs and kwargs["uuid"] == "my-file":
                self.assertEqual({"device": mock_device.uuid, "uuid": "my-file"}, kwargs)
                out.first.return_value = mock_file
            else:
                self.assertEqual(mock_device.uuid, kwargs["device"])
                self.assertIn(kwargs["uuid"], filesystem)
                out.first.return_value = filesystem[kwargs["uuid"]]
            return out

        self.query_file.filter_by.side_effect = handle_file_query

        expected_result = can_not_move_dir_into_itself
        actual_result = file.move(
            {
                "device_uuid": mock_device.uuid,
                "file_uuid": "my-file",
                "new_filename": "new-name",
                "new_parent_dir_uuid": "10",
            },
            "user",
        )

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with(mock_device.uuid)
        mock_device.check_access.assert_called_with("user")

    def test__user_endpoint__file_move__successful(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True
        mock_file = mock.MagicMock()
        mock_file.is_changeable = True
        mock_file.is_directory = True
        mock_file.uuid = "3"
        filesystem = {}
        dir_mock = mock.MagicMock()
        dir_mock.parent_dir_uuid = None
        dir_mock.uuid = "0"
        filesystem.update({str(0): dir_mock})

        self.query_device.get.return_value = mock_device

        def handle_file_query(**kwargs):
            out = mock.MagicMock()
            if "filename" in kwargs:
                self.assertEqual({"device": mock_device.uuid, "filename": "new-name", "parent_dir_uuid": "0"}, kwargs)
                out.first.return_value = None
            elif "uuid" in kwargs and kwargs["uuid"] == "my-file":
                self.assertEqual({"device": mock_device.uuid, "uuid": "my-file"}, kwargs)
                out.first.return_value = mock_file
            else:
                self.assertEqual(mock_device.uuid, kwargs["device"])
                self.assertIn(kwargs["uuid"], filesystem)
                out.first.return_value = filesystem[kwargs["uuid"]]
            return out

        self.query_file.filter_by.side_effect = handle_file_query

        expected_result = mock_file.serialize
        actual_result = file.move(
            {
                "device_uuid": mock_device.uuid,
                "file_uuid": "my-file",
                "new_filename": "new-name",
                "new_parent_dir_uuid": "0",
            },
            "user",
            mock_device,
        )

        self.assertEqual(expected_result, actual_result)
        self.assertEqual("new-name", mock_file.filename)
        mock.wrapper.session.commit.assert_called_with()
        mock.m.contact_user.assert_called_with(
            "user",
            {
                "notify-id": "file-update",
                "origin": "update",
                "device_uuid": mock_device.uuid,
                "data": {"created": [], "deleted": [], "changed": [mock_file.uuid]},
            },
        )

    def test__user_endpoint__file_update__file_not_found(self):
        mock_device = mock.MagicMock()

        self.query_file.filter_by().first.return_value = None

        expected_result = file_not_found
        actual_result = file.update(
            {"device_uuid": mock_device.uuid, "file_uuid": "my-file", "content": "test"}, "user", mock_device
        )

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid="my-file")

    def test__user_endpoint__file_update__directories_can_not_be_updated(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True
        mock_file = mock.MagicMock()
        mock_file.is_directory = True

        self.query_device.get.return_value = mock_device
        self.query_file.filter_by().first.return_value = mock_file

        expected_result = directories_can_not_be_updated
        actual_result = file.update(
            {"device_uuid": mock_device.uuid, "file_uuid": "my-file", "content": "test"}, "user"
        )

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with(mock_device.uuid)
        mock_device.check_access.assert_called_with("user")
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid="my-file")

    def test__user_endpoint__file_update__file_not_changeable(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True
        mock_file = mock.MagicMock()
        mock_file.is_directory = False
        mock_file.is_changeable = False

        self.query_device.get.return_value = mock_device
        self.query_file.filter_by().first.return_value = mock_file

        expected_result = file_not_changeable
        actual_result = file.update(
            {"device_uuid": mock_device.uuid, "file_uuid": "my-file", "content": "test"}, "user"
        )

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with(mock_device.uuid)
        mock_device.check_access.assert_called_with("user")
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid="my-file")

    def test__user_endpoint__file_update__successful(self):
        mock_device = mock.MagicMock()
        mock_file = mock.MagicMock()
        mock_file.is_directory = False
        mock_file.is_changeable = True

        self.query_file.filter_by().first.return_value = mock_file

        expected_result = mock_file.serialize
        actual_result = file.update(
            {"device_uuid": mock_device.uuid, "file_uuid": mock_file.uuid, "content": "test"}, "user", mock_device
        )

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid=mock_file.uuid)
        self.assertEqual("test", mock_file.content)
        mock.wrapper.session.commit.assert_called_with()
        mock.m.contact_user.assert_called_with(
            "user",
            {
                "notify-id": "file-update",
                "origin": "update",
                "device_uuid": mock_device.uuid,
                "data": {"created": [], "deleted": [], "changed": [mock_file.uuid]},
            },
        )

    def test__user_endpoint__file_delete__file_not_found(self):
        mock_device = mock.MagicMock()

        self.query_file.filter_by().first.return_value = None

        expected_result = file_not_found
        actual_result = file.delete_file({"device_uuid": mock_device.uuid, "file_uuid": "my-file"}, "user", mock_device)

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid="my-file")

    def test__user_endpoint__normal_file_delete__file_not_changeable(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True
        mock_file = mock.MagicMock()
        mock_file.is_changeable = False
        mock_file.is_directory = False

        self.query_device.get.return_value = mock_device
        self.query_file.filter_by().first.return_value = mock_file

        expected_result = file_not_changeable
        actual_result = file.delete_file({"device_uuid": mock_device.uuid, "file_uuid": mock_file.uuid}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with(mock_device.uuid)
        mock_device.check_access.assert_called_with("user")
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid=mock_file.uuid)

    def test__user_endpoint__normal_file_delete__successful(self):
        mock_device = mock.MagicMock()
        mock_file = mock.MagicMock()
        mock_file.is_directory = False

        self.query_file.filter_by().first.return_value = mock_file

        expected_result = success
        actual_result = file.delete_file(
            {"device_uuid": mock_device.uuid, "file_uuid": mock_file.uuid}, "user", mock_device
        )

        self.assertEqual(expected_result, actual_result)
        self.query_file.filter_by.assert_called_with(device=mock_device.uuid, uuid=mock_file.uuid)
        mock.wrapper.session.delete.assert_called_with(mock_file)
        mock.wrapper.session.commit.assert_called_with()

    def test__user_endpoint__directory_file_delete__file_not_changeable(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True
        mock_file = mock.MagicMock()
        mock_file.is_changeable = True
        mock_file.is_directory = True
        mock_file.uuid = "AC"

        filesystem = {}
        filesystem_after_deletion = {}

        def create_file(uuid, parent_dir_uuid, is_changeable, is_directory, add_to_filesystem_a_d):
            file_mock = mock.MagicMock()
            file_mock.uuid = uuid
            file_mock.parent_dir_uuid = parent_dir_uuid
            file_mock.is_changeable = is_changeable
            file_mock.is_directory = is_directory
            filesystem.update({uuid: file_mock})
            if add_to_filesystem_a_d:
                filesystem_after_deletion.update({uuid: file_mock})

        create_file("0", None, False, True, True)
        create_file("A", "0", True, True, True)
        create_file("AA", "A", True, False, True)
        create_file("AB", "A", True, False, True)
        create_file("AC", "A", True, True, True)
        create_file("AAA", "AC", True, True, False)
        create_file("AAB", "AC", True, False, True)
        create_file("AAC", "AC", False, False, True)
        create_file("AAD", "AC", True, False, False)
        create_file("AD", "A", True, False, True)
        create_file("AE", "0", False, False, True)

        self.query_device.get.return_value = mock_device

        def handle_file_query(**kwargs):
            out = mock.MagicMock()
            if "uuid" in kwargs:
                self.assertEqual({"device": mock_device.uuid, "uuid": "AC"}, kwargs)
                out.first.return_value = mock_file
            elif "parent_dir_uuid" in kwargs:
                self.assertIn(kwargs["parent_dir_uuid"], filesystem)
                out.all.return_value = [
                    v for _, v in filesystem.items() if v.parent_dir_uuid == kwargs["parent_dir_uuid"]
                ]
            return out

        def delete_file(file):
            del filesystem[file.uuid]

        self.query_file.filter_by.side_effect = handle_file_query
        mock.wrapper.session.delete.side_effect = delete_file
        self.query_device.get.return_value = mock_device

        expected_result = file_not_changeable
        actual_result = file.delete_file({"device_uuid": mock_device.uuid, "file_uuid": "AC"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.assertEqual(filesystem, filesystem_after_deletion)
        self.query_device.get.assert_called_with(mock_device.uuid)
        mock_device.check_access.assert_called_with("user")
        mock.m.contact_user.assert_called_with(
            "user",
            {
                "notify-id": "file-update",
                "origin": "delete",
                "device_uuid": mock_device.uuid,
                "data": {"created": [], "deleted": ["AAA", "AAD"], "changed": []},
            },
        )

    def test__user_endpoint__directory_file_delete__successful(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True
        mock_file = mock.MagicMock()
        mock_file.is_changeable = True
        mock_file.is_directory = True
        mock_file.uuid = "AC"

        filesystem = {}
        filesystem_after_deletion = {}

        def create_file(uuid, parent_dir_uuid, is_changeable, is_directory, add_to_filesystem_a_d):
            file_mock = mock.MagicMock()
            file_mock.uuid = uuid
            file_mock.parent_dir_uuid = parent_dir_uuid
            file_mock.is_changeable = is_changeable
            file_mock.is_directory = is_directory
            filesystem.update({uuid: file_mock})
            if add_to_filesystem_a_d:
                filesystem_after_deletion.update({uuid: file_mock})

        create_file("0", None, False, True, True)
        create_file("A", "0", True, True, True)
        create_file("AA", "A", True, False, True)
        create_file("AB", "A", True, False, True)
        create_file("AC", "A", True, True, False)
        create_file("AAA", "AC", True, True, False)
        create_file("AAB", "AC", True, False, False)
        create_file("AAC", "AC", True, False, False)
        create_file("AAD", "AC", True, False, False)
        create_file("AD", "A", True, False, True)
        create_file("AE", "0", False, False, True)

        self.query_device.get.return_value = mock_device

        def handle_file_query(**kwargs):
            out = mock.MagicMock()
            if "uuid" in kwargs:
                self.assertEqual({"device": mock_device.uuid, "uuid": "AC"}, kwargs)
                out.first.return_value = mock_file
            elif "parent_dir_uuid" in kwargs:
                self.assertIn(kwargs["parent_dir_uuid"], filesystem)
                out.all.return_value = [
                    v for _, v in filesystem.items() if v.parent_dir_uuid == kwargs["parent_dir_uuid"]
                ]
            return out

        def delete_file(file):
            del filesystem[file.uuid]

        self.query_file.filter_by.side_effect = handle_file_query
        mock.wrapper.session.delete.side_effect = delete_file
        self.query_device.get.return_value = mock_device

        expected_result = success
        actual_result = file.delete_file({"device_uuid": mock_device.uuid, "file_uuid": "AC"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.assertEqual(filesystem, filesystem_after_deletion)
        self.query_device.get.assert_called_with(mock_device.uuid)
        mock_device.check_access.assert_called_with("user")
        mock.m.contact_user.assert_called_with(
            "user",
            {
                "notify-id": "file-update",
                "origin": "delete",
                "device_uuid": mock_device.uuid,
                "data": {"created": [], "deleted": ["AAA", "AAD", "AAC", "AAB", "AC"], "changed": []},
            },
        )

    def test__user_endpoint__file_create__device_not_found(self):
        self.query_device.get.return_value = None

        expected_result = device_not_found
        actual_result = file.create_file({"device_uuid": "my-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my-device")

    def test__user_endpoint__file_create__permission_denied(self):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = False

        self.query_device.get.return_value = mock_device

        expected_result = permission_denied
        actual_result = file.create_file({"device_uuid": "my-device"}, "user")

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with("my-device")
        mock_device.check_access.assert_called_with("user")

    def test__user_endpoint__file_create__file_already_exists(self):
        mock_device = mock.MagicMock()

        self.query_func_count.filter_by().scalar.return_value = 1

        expected_result = file_already_exists
        actual_result = file.create_file(
            {
                "device_uuid": mock_device.uuid,
                "filename": "test-file",
                "content": "some random content here",
                "parent_dir_uuid": "0",
                "is_directory": False,
                "is_changeable": True,
            },
            "user",
            mock_device,
            {"device_uuid": mock_device.uuid, "filename": "test-file", "content": "some random content here"},
            "user",
            mock_device,
        )

        self.assertEqual(expected_result, actual_result)
        self.sqlalchemy_func.count.assert_called_with(File.uuid)
        self.query_func_count.filter_by.assert_called_with(
            device=mock_device.uuid, filename="test-file", parent_dir_uuid="0"
        )

    @patch("resources.file.File.create")
    def test__user_endpoint__file_create__successful(self, file_create_patch):
        mock_device = mock.MagicMock()

        self.query_func_count.filter_by().scalar.return_value = 0

        expected_result = file_create_patch().serialize
        actual_result = file.create_file(
            {
                "device_uuid": mock_device.uuid,
                "filename": "test-file",
                "content": "some random content here",
                "is_directory": False,
                "is_changeable": True,
                "parent_dir_uuid": "0",
            },
            "user",
            mock_device,
        )

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with(mock_device.uuid)
        mock_device.check_access.assert_called_with("user")
        self.sqlalchemy_func.count.assert_called_with(File.uuid)
        self.query_func_count.filter_by.assert_called_with(
            device=mock_device.uuid, filename="test-file", parent_dir_uuid="0"
        )
        file_create_patch.assert_called_with(
            mock_device.uuid, "test-file", "some random content here", "0", False, True
        )
        mock.m.contact_user.assert_called_with(
            "user",
            {
                "notify-id": "file-update",
                "origin": "create",
                "device_uuid": mock_device.uuid,
                "data": {"created": [file_create_patch().uuid], "deleted": [], "changed": []},
            },
        )

    @patch("resources.file.File.create")
    def test__user_endpoint__file_create__directory_can_not_have_textcontent(self, file_create_patch):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True

        self.query_device.get.return_value = mock_device
        self.query_func_count.filter_by().scalar.return_value = 0

        expected_result = directory_can_not_have_textcontent
        actual_result = file.create_file(
            {
                "device_uuid": mock_device.uuid,
                "filename": "test-file",
                "content": "some random content here",
                "is_changeable": True,
                "is_directory": True,
                "parent_dir_uuid": "0",
            },
            "user",
            mock_device,
        )

        self.assertEqual(expected_result, actual_result)
        self.sqlalchemy_func.count.assert_called_with(File.uuid)
        self.query_func_count.filter_by.assert_called_with(
            device=mock_device.uuid, filename="test-file", parent_dir_uuid="0"
        )

    @patch("resources.file.File.create")
    def test__user_endpoint__file_create__no_parent_dir(self, file_create_patch):
        mock_device = mock.MagicMock()
        mock_device.check_access.return_value = True

        self.query_file.filter_by().first.return_value = None
        self.query_device.get.return_value = mock_device
        self.query_func_count.filter_by().scalar.return_value = 0

        expected_result = parent_directory_not_found
        actual_result = file.create_file(
            {
                "device_uuid": mock_device.uuid,
                "filename": "test-file",
                "content": "some random content here",
                "is_changeable": True,
                "is_directory": True,
                "parent_dir_uuid": "0",
            },
            "user",
        )

        self.assertEqual(expected_result, actual_result)
        self.query_device.get.assert_called_with(mock_device.uuid)
        mock_device.check_access.assert_called_with("user")
        self.sqlalchemy_func.count.assert_called_with(File.uuid)
        self.query_func_count.filter_by.assert_called_with(
            device=mock_device.uuid, filename="test-file", parent_dir_uuid="0"
        )
        self.query_func_count.filter_by.assert_called_with(device=mock_device.uuid, filename="testfile")
        file_create_patch.assert_called_with(mock_device.uuid, "testfile", "some random content here")
