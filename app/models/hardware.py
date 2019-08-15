from typing import Union, Dict, Any
from uuid import uuid4

from sqlalchemy import Column, String

from app import wrapper


class Hardware(wrapper.Base):
    """
    This is the hardware-model for cryptic-game
    """

    __tablename__: str = "device_hardware"

    uuid: Union[str, Column] = Column(String(36), primary_key=True, unique=True)
    device_uuid: Union[str, Column] = Column(String(36), nullable=False)
    hardware_element: Union[str, Column] = Column(String(40), nullable=False)
    hardware_typ: Union[str, Column] = Column(String(36), nullable=False)

    @property
    def serialize(self) -> Dict[str, Any]:
        _: str = self.uuid
        d = self.__dict__.copy()

        del d["_sa_instance_state"]

        return d

    @staticmethod
    def create(device: str, hardware: str, hardware_typ: str) -> "Hardware":
        hardware_element: Hardware = Hardware(
            uuid=str(uuid4()), device_uuid=device, hardware_element=hardware, hardware_typ=hardware_typ
        )

        wrapper.session.add(hardware_element)
        wrapper.session.commit()

        return hardware_element
