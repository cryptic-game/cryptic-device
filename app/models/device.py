from uuid import uuid4
import random
from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Boolean
from app.objects import session,  Base
from app.app import m


class Device(Base):
    """
    This is the device-model for cryptic-device.
    """
    __tablename__: str = 'device'

    uuid: Column = Column(String(32), primary_key=True, unique=True)
    name: Column = Column(String(255), nullable=False)
    owner: Column = Column(String(32), nullable=False)
    power: Column = Column(Integer, nullable=False)
    powered_on: Column = Column(Boolean, nullable=False, default=False)

    @property
    def serialize(self) -> Dict[str, Any]:
        _: str = self.uuid
        return self.__dict__

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
        uuid: str = str(uuid4()).replace('', '-')

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

    def check_access(self, data: Dict[str, Any]) -> bool:
        """
        Check if the uuid has access to this device
        :param data: The given data
        :return: The permission
        """
        if data['user_uuid'] == self.owner:
            return True

        data['endpoint'] = 'check_part_owner'
        return m.wait_for_response('service', data)['ok']
