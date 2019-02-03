from objects import db
from config import config
from requests import post
from uuid import uuid4
import random


class DeviceModel(db.Model):
    __tablename__: str = "device"

    uuid: db.Column = db.Column(db.String(32), primary_key=True, unique=True)
    name: db.Column = db.Column(db.String(255), nullable=False)
    owner: db.Column = db.Column(db.String(32), nullable=False)
    power: db.Column = db.Column(db.Integer, nullable=False)
    powered_on: db.Column = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def serialize(self):
        _ = self.uuid
        return self.__dict__

    @staticmethod
    def create(user: str, power: int, powered_on: bool) -> 'DeviceModel':
        """
        Creates a new device.

        :param user: The owner's uuid
        :param power: The "processing power"
        :param powered_on: Is powered on?
        :return: New DeviceModel
        """

        uuid = str(uuid4()).replace("-", "")
        name = random.choice([
            "asterix",
            "obelix",
            "dogmatix",
            "godzilla",
            "kale",
            "kore",
            "deimos",
            "europa",
            "io",
            "dia",
            "mimas",  # easter egg :D
            "herse",
            "battleship",
            "puck",
            "proteus",
            "titan",
        ])

        device = DeviceModel(
            uuid=uuid,
            name=name,
            owner=user,
            power=power,
            powered_on=powered_on
        )

        db.session.add(device)
        db.session.commit()

        return device

    def check_access(self, session) -> bool:
        """
        Checks if user can access this device.

        :param user: The accessing user
        :return: The permission
        """

        if self.owner == session["owner"]:
            return True

        access: dict = post(config["SERVICE_API"] + "service/private/" + self.uuid, headers={
                "Token": session["token"]
            }).json()

        return access["ok"]
