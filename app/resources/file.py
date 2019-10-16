from typing import Optional

from sqlalchemy import func

from app import m, wrapper
from models.device import Device
from models.file import File
from schemes import (
    file_already_exists,
    file_not_found,
    device_not_found,
    permission_denied,
    success,
    requirement_file,
    requirement_file_delete,
    requirement_file_move,
    requirement_file_update,
    requirement_file_create,
    directories_can_not_be_updated,
    directory_can_not_have_textcontent,
    parent_directory_not_found,
    file_not_changeable,
    can_not_move_dir_into_itself,
    basic_file_requirement,
    parent_dir_does_not_exist,
)


@m.user_endpoint(path=["file", "all"], requires=basic_file_requirement)
def list_files(data: dict, user: str) -> dict:
    """
    Get all files of a device.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found

    if not device.check_access(user):
        return permission_denied

    parent_dir_uuid = data["parent_dir_uuid"]

    return {
        "files": [
            f.serialize
            for f in wrapper.session.query(File).filter_by(device=device.uuid, parent_dir_uuid=parent_dir_uuid).all()
        ]
    }


@m.user_endpoint(path=["file", "info"], requires=requirement_file)
def file_info(data: dict, user: str) -> dict:
    """
    Get information about a file
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device_uuid: str = data["device_uuid"]
    file_uuid: str = data["file_uuid"]

    device: Optional[Device] = wrapper.session.query(Device).get(device_uuid)

    if device is None:
        return device_not_found

    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).filter_by(device=device_uuid, uuid=file_uuid).first()

    if file is None:
        return file_not_found

    return file.serialize


@m.user_endpoint(path=["file", "move"], requires=requirement_file_move)
def move(data: dict, user: str) -> dict:
    device_uuid: str = data["device_uuid"]
    file_uuid = data["file_uuid"]
    new_filename = data["new_filename"]
    new_parent_dir_uuid = data["new_parent_dir_uuid"]

    device: Optional[Device] = wrapper.session.query(Device).get(device_uuid)

    if device is None:
        return device_not_found
    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).filter_by(device=device_uuid, uuid=file_uuid).first()

    if file is None:
        return file_not_found

    if not file.is_changeable:
        return file_not_changeable

    target_file: Optional[File] = wrapper.session.query(File).filter_by(
        device=device_uuid, filename=new_filename, parent_dir_uuid=new_parent_dir_uuid
    ).first()
    if target_file is not None:
        return file_already_exists

    target_dir: Optional[File] = (
        wrapper.session.query(File).filter_by(device=device_uuid, is_directory=True, uuid=new_parent_dir_uuid).first()
    )
    if target_dir is None:
        return parent_directory_not_found

    if file.is_directory:
        parent_to_check: Optional[File] = wrapper.session.query(File).filter_by(
            device=device_uuid, uuid=new_parent_dir_uuid
        ).first()
        while parent_to_check.parent_dir_uuid is not None:
            if parent_to_check.uuid == file.uuid:
                return can_not_move_dir_into_itself
            parent_to_check: Optional[File] = wrapper.session.query(File).filter_by(
                device=device_uuid, uuid=parent_to_check.parent_dir_uuid
            ).first()

    file.filename = new_filename
    file.parent_dir_uuid = new_parent_dir_uuid
    wrapper.session.commit()

    return file.serialize


@m.user_endpoint(path=["file", "update"], requires=requirement_file_update)
def update(data: dict, user: str) -> dict:
    """
    Update the content of a file.

    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """

    device_uuid: str = data["device_uuid"]
    file_uuid = data["file_uuid"]
    content = data["content"]

    device: Optional[Device] = wrapper.session.query(Device).get(device_uuid)

    if device is None:
        return device_not_found
    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).filter_by(device=device_uuid, uuid=file_uuid).first()

    if file is None:
        return file_not_found

    if file.is_directory:
        return directories_can_not_be_updated

    if not file.is_changeable:
        return file_not_changeable

    file.content = content
    wrapper.session.commit()

    return file.serialize


@m.user_endpoint(path=["file", "delete"], requires=requirement_file_delete)
def delete_file(data: dict, user: str) -> dict:
    """
    Delete a file.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """

    device_uuid: str = data["device_uuid"]
    file_uuid: str = data["file_uuid"]

    device: Optional[Device] = wrapper.session.query(Device).get(device_uuid)

    if device is None:
        return device_not_found

    if not device.check_access(user):
        return permission_denied

    file: Optional[File] = wrapper.session.query(File).filter_by(device=device_uuid, uuid=file_uuid).first()

    if file is None:
        return file_not_found

    if not file.is_changeable:
        return file_not_changeable

    if file.is_directory:
        stack_to_delete = []
        dirs = [file]
        while len(dirs) > 0:
            dir_to_check = dirs.pop()
            stack_to_delete.append(dir_to_check)
            files_in_dir: list = wrapper.session.query(File).filter_by(
                device=device_uuid, parent_dir_uuid=dir_to_check.uuid
            ).all()
            for child_file in files_in_dir:
                if child_file.is_directory:
                    dirs.append(child_file)
                else:
                    stack_to_delete.append(child_file)
    else:
        stack_to_delete = [file]

    error_while_deleting = None
    while stack_to_delete:
        file_to_delete = stack_to_delete.pop()
        if file_to_delete.is_changeable:
            wrapper.session.delete(file_to_delete)
        else:
            error_while_deleting = file_not_changeable
            break

    wrapper.session.commit()

    if error_while_deleting:
        return error_while_deleting
    return success


@m.user_endpoint(path=["file", "create"], requires=requirement_file_create)
def create_file(data: dict, user: str) -> dict:
    """
    Create a new file.
    :param data: The given data.
    :param user: The user uuid.
    :return: The response
    """
    device: Optional[Device] = wrapper.session.query(Device).get(data["device_uuid"])

    if device is None:
        return device_not_found

    if not device.check_access(user):
        return permission_denied

    filename: str = data["filename"]
    content: str = data["content"]
    is_directory: bool = data["is_directory"]
    parent_dir_uuid: str = data["parent_dir_uuid"]

    file_count: int = wrapper.session.query(func.count(File.uuid)).filter_by(
        device=device.uuid, filename=filename, parent_dir_uuid=parent_dir_uuid
    ).scalar()

    if file_count > 0:
        return file_already_exists

    parent_dir: File = wrapper.session.query(File).filter_by(
        device=device.uuid, uuid=parent_dir_uuid, is_directory=True
    ).first()
    if not parent_dir:
        return parent_dir_does_not_exist

    if is_directory and content != "":
        return directory_can_not_have_textcontent

    file: File = File.create(device.uuid, filename, content, parent_dir_uuid, is_directory, True)

    return file.serialize
