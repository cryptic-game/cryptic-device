from typing import Union, Optional
from uuid import uuid4

from sqlalchemy import Column, String, Boolean

from app import wrapper

CONTENT_LENGTH = 255


class File(wrapper.Base):
    """
    This is the file-model for cryptic-device.
    """

    __tablename__: str = "device_file"

    uuid: Union[Column, str] = Column(String(36), primary_key=True, unique=True)
    device: Union[Column, str] = Column(String(36), nullable=False)
    filename: Union[Column, str] = Column(String(255, collation="utf8_bin"), nullable=False)
    content: Union[Column, str] = Column(String(CONTENT_LENGTH), nullable=False)
    is_directory: Union[Column, bool] = Column(Boolean, nullable=False, default=False)
    parent_dir_uuid: Union[Column, str] = Column(String(36))
    is_changeable: [Union, bool] = Column(Boolean, nullable=False, default=True)

    @property
    def serialize(self) -> dict:
        _: str = self.uuid
        d: dict = self.__dict__.copy()

        del d["_sa_instance_state"]

        return d

    @staticmethod
    def create(
        device: str,
        filename: str,
        content: str,
        parent_dir_uuid: Optional[str],
        is_directory: bool,
        is_changeable: bool,
    ) -> "File":
        """
        Creates a new file
        :param device: The device's uuid
        :param filename: The name of the new file
        :param parent_dir_uuid: The parent directory (uuid) of the new file
        :param content: The content of the new file
        :param is_directory: If the new file is a directory
        :param is_changeable: If the new file is changeable by the user (move, filename, content)
        :return: New File
        """

        uuid = str(uuid4())

        # Return a new file
        file: File = File(
            uuid=uuid,
            device=device,
            filename=filename,
            content=content,
            parent_dir_uuid=parent_dir_uuid,
            is_directory=is_directory,
            is_changeable=is_changeable,
        )

        wrapper.session.add(file)
        wrapper.session.commit()

        return file
