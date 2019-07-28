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

    uuid: Union[str, Column] = Column(String(36), primary_key=True, unique=True)
    device_uuid: Union[str, Column] = Column(String(36))
    hardware_element: Union[str, Column] = Column(String(40))
    hardware_typ: Union[str, Column] = Column(String(36))

    @staticmethod
    def create(device: str, hardware: str, hardware_typ: str) -> "Hardware":

        hd: Hardware = Hardware(
            uuid=str(uuid4()), device_uuid=device, hardware_element=hardware, hardware_typ=hardware_typ
        )

        wrapper.session.add(hd)
        wrapper.session.commit()

        return hd
