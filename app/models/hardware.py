import random
from typing import Dict, Any, Union
from uuid import uuid4

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.expression import func, select

from app import m, wrapper


class Hardware(wrapper.Base):
    """
    This is the hardware-model for cryptic-game
    """

    __tablename__: str = "hardware"

    device_uuid: Union[str, Column] = Column(String(36))
    hardware_element: Union[str, Column] = Column(String(40))

    @staticmethod
    def create(device: str, hardware: str) -> "Device":

        hd: Hardware = Hardware(device_uuid=device, hardware_element=hardware)

        wrapper.session.add(hd)
        wrapper.session.commit()
