from objects import db
from uuid import uuid4

CONTENT_LENGTH = 255


class FileModel(db.Model):
    __tablename__: str = "file"

    uuid: db.Column = db.Column(db.String(32), primary_key=True, unique=True)
    device: db.Column = db.Column(db.String(32), nullable=False)  # TODO add relationship between
    filename: db.Column = db.Column(db.String(255), nullable=False)
    content: db.Column = db.Column(db.String(CONTENT_LENGTH), nullable=False)

    @property
    def serialize(self):
        _ = self.uuid
        return self.__dict__

    @staticmethod
    def create(device: str, filename: str, content: str) -> 'FileModel':
        """
        Creates a new device.

        :param device: The device's uuid
        :param filename: The name of the new file
        :param content: The content of the new file
        :return: New FileModel
        """

        uuid = str(uuid4()).replace("-", "")

        file = FileModel(
            uuid=uuid,
            device=device,
            filename=filename,
            content=content,
        )

        db.session.add(file)
        db.session.commit()

        return file

