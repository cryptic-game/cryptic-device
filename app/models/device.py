import random
from typing import Dict, Any, Union
from uuid import uuid4

from sqlalchemy import Column, Integer, String, Boolean

from app import m
from objects import session, Base


class Device(Base):
    """
    This is the device-model for cryptic-device.
    """
    __tablename__: str = 'device'

    uuid: Union[Column, str] = Column(String(32), primary_key=True, unique=True)
    name: Union[Column, str] = Column(String(255), nullable=False)
    owner: Union[Column, str] = Column(String(32), nullable=False)
    power: Union[Column, int] = Column(Integer, nullable=False)
    powered_on: Union[Column, bool] = Column(Boolean, nullable=False, default=False)

    @property
    def serialize(self) -> Dict[str, Any]:
        _: str = self.uuid
        d = self.__dict__

        del d['_sa_instance_state']

        return d

    @staticmethod
    def create(user: str, power: int, powered_on: bool) -> 'Device':
        """
        Creates a new device.
        :param user: The owner's uuid
        :param power: The "processing power"
        :param powered_on: Is powered on?
        :return: New Device
        """

        # Create a new uuid for the device
        uuid: str = str(uuid4())

        # Get a random name for the device
        name: str = random.choice([
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
            "quint"
        ])

        # Return a new device
        device: Device = Device(
            uuid=uuid,
            name=name,
            owner=user,
            power=power,
            powered_on=powered_on
        )

        session.add(device)
        session.commit()

        return device

    def check_access(self, user: str) -> bool:
        """
        Check if the uuid has access to this device
        :param user:
        :return: The permission
        """
        if user == self.owner:
            return True

        return m.contact_microservice("service", ["check_part_owner"], {"user_uuid": user})["ok"]
