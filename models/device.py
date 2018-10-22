from database import db
import uuid


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    owner = db.Column(db.Integer, nullable=False)
    power = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(32), nullable=False, unique=True)

    def __init__(self, owner, address, power, networks=None):
        self.owner = owner
        self.power = power
        print("Test")
        if not address:
            address = str(uuid.uuid4()).replace("-", "")
        self.address = address
        self.networks = 0

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
    def create(user, address=None, power=1, networks=None) -> 'Device':
        """
        Creates a new device for a specified user.

        :param user: The owner's id
        :param power: The power of the device
        :param address: The network address of the device
        :return: New device
        """

        device = Device(user, address, power, networks)

        db.session.add(device)
        db.session.commit()

        return device

    @staticmethod
    def get_by_id(id: int) -> "Device":
        """
        This function finds a device based on its unique id.

        :param id: Unique device id to search for.
        :return: A device based on a id.
        """
        return Device.query.filter_by(id=id).first()

    @staticmethod
    def get_by_owner(owner: int) -> "Device":
        """
        This function finds a device based on an User id.

        :param id: Unique User id to search for assigned devices.
        :return: A list of devices based on the User id.
        """
        return Device.query.filter_by(id=id).first()

    def as_private_simple_dict(self) -> dict:
        """
        Returns a dictionary with basic PRIVATE information about this device.
        :return: dictionary with basic information
        """

        return {
            "device_id": self.id,
            "device_owner": self.owner,
            "power": self.power,
            "address": self.address
        }

    def as_public_simple_dict(self) -> dict:
        """
        Returns a dictionary with basic PUBLIC information about this device.
        :return: dictionary with basic information
        """

        return {
            "device_id": self.id,
            "device_owner": self.owner,
            "power": self.power
        }
