from typing import Union
from uuid import uuid4

from sqlalchemy import Column, String

from app import m, wrapper

CONTENT_LENGTH = 255


class File(wrapper.Base):
    """
    This is the file-model for cryptic-device.
    """
    __tablename__: str = 'file'

    uuid: Union[Column, str] = Column(String(36), primary_key=True, unique=True)
    device: Union[Column, str] = Column(String(36), nullable=False)
    filename: Union[Column, str] = Column(String(255), nullable=False)
    content: Union[Column, str] = Column(String(CONTENT_LENGTH), nullable=False)

    @property
    def serialize(self) -> dict:
        _: str = self.uuid
        d: dict = self.__dict__

        del d['_sa_instance_state']

        return d

    @staticmethod
    def create(device: str, filename: str, content: str) -> 'File':
        """
        Creates a new file
        :param device: The device's uuid
        :param filename: The name of the new file
        :param content: The content of the new file
        :return: New File
        """

        uuid = str(uuid4())

        # Return a new file
        file: File = File(
            uuid=uuid,
            device=device,
            filename=filename,
            content=content
        )

        wrapper.session.add(file)
        wrapper.session.commit()

        return file
