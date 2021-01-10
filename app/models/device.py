import random
from typing import Dict, Any, Union, Optional
from uuid import uuid4

from sqlalchemy import Column, String, Boolean
from sqlalchemy.sql.expression import func, and_

from app import m, wrapper


class Device(wrapper.Base):
    """
    This is the device-model for cryptic-device.
    """

    __tablename__: str = "device_device"

    uuid: Union[Column, str] = Column(String(36), primary_key=True, unique=True)
    name: Union[Column, str] = Column(String(255), nullable=False)
    owner: Union[Column, str] = Column(String(36), nullable=False)
    powered_on: Union[Column, bool] = Column(Boolean, nullable=False, default=False)
    starter_device: Union[Column, bool] = Column(Boolean, nullable=False, default=False)

    @property
    def serialize(self) -> Dict[str, Any]:
        _: str = self.uuid
        d = self.__dict__.copy()

        del d["_sa_instance_state"]

        return d

    @staticmethod
    def create_starter_device(user: str, powered_on: bool) -> "Device":
        return Device.create(user, powered_on, True)

    @staticmethod
    def create(user: str, powered_on: bool, starter_device: Optional[bool] = False) -> "Device":
        """
        Creates a new device.
        :param user: The owner's uuid
        :param powered_on: Is powered on?
        :return: New Device
        """

        # Create a new uuid for the device
        uuid: str = str(uuid4())

        # Get a random name for the device
        name: str = random.choice(
            [
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
                "quint",
            ]
        )

        # Return a new device
        device: Device = Device(uuid=uuid, name=name, owner=user, powered_on=powered_on, starter_device=starter_device)

        wrapper.session.add(device)
        wrapper.session.commit()

        return device

    def check_access(self, user: str) -> bool:
        """
        Check if the uuid has access to this device
        :param user:
        :return: The permission
        """
        if user == self.owner:
            return True

        return m.contact_microservice("service", ["check_part_owner"], {"user_uuid": user, "device_uuid": self.uuid})[
            "ok"
        ]

    @staticmethod
    def random(user: str) -> Optional["Device"]:
        return (
            wrapper.session.query(Device)
            .filter(and_(Device.owner != user, Device.powered_on))
            .order_by(func.random())
            .first()
        )
