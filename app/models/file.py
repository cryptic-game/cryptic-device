from uuid import uuid4
from sqlalchemy import Column, String
from objects import session, Base

CONTENT_LENGTH = 255


class File(Base):
    """
    This is the file-model for cryptic-device.
    """
    __tablename__: str = 'file'

    uuid: Column = Column(String(32), primary_key=True, unique=True)
    device: Column = Column(String(32), nullable=False)
    filename: Column = Column(String(255), nullable=False)
    content: Column = Column(String(CONTENT_LENGTH), nullable=False)

    @property
    def serialize(self) -> dict:
        _ = self.uuid
        return self.__dict__

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

        session.add(file)
        session.commit()

        return file
