from database import db


class Device(db.Model):
    id = db.Column(db.Integer, autoincrement=True, unique=True)

    def __init__(self):
	pass

    def delete(self) -> None:
        """
        Deletes this session.

        :return: None
        """

        db.session.delete(self)
        db.session.commit()

    def commit(self) -> None:
        """
        Commits changes to the database.

        :return: None
        """

        db.session.commit()

    @staticmethod
    def create() -> 'Device':
        """
        Creates a new device for a specified user.

        :param user: The owner's id
        :return: New session
        """

	device = Device()

        db.session.add(device)
        db.session.commit()

        return session
