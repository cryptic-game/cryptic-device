from database import db


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    owner = db.Column(db.Integer, nullable=False)
    power = db.Column(db.Float, nullable=False)
    networks = db.Column(db.Integer, db.ForeignKey("network.id"), nullable=False)

    def __init__(self, owner, power):
        self.owner = owner
        self.power = power

    def delete(self) -> None:
        """
        Deletes this device.

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
    def create(user, power) -> 'Device':
        """
        Creates a new device for a specified user.

        :param user: The owner's id
		:param power: The power of the device
        :return: New device
        """

        device = Device(user, power)

        db.session.add(device)
        db.session.commit()

        return device
