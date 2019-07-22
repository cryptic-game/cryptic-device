import random
from typing import Dict, Any, Union, Tuple
from uuid import uuid4

from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy.sql.expression import func, select

from app import m, wrapper


class Workload(wrapper.Base):
    """
    This is the workload-model for cryptic-game
    """

    __tablename__: str = "workload"

    device_uuid: Union[str, Column] = Column(String(36))
    performance_cpu: Union[float, Column] = Column(Float)
    performance_gpu: Union[float, Column] = Column(Float)
    performance_ram: Union[float, Column] = Column(Float)
    performance_disk: Union[float, Column] = Column(Float)
    performance_network: Union[float, Column] = Column(Float)

    usage_cpu: Union[float, Column] = Column(Float)
    usage_gpu: Union[float, Column] = Column(Float)
    usage_ram: Union[float, Column] = Column(Float)
    usage_disk: Union[float, Column] = Column(Float)
    usage_network: Union[float, Column] = Column(Float)

    @staticmethod
    def create(device: str, attributes: Tuple[float, float, float, float, float]) -> "Workload":

        work: Workload = Workload(
            device_uuid=device,
            performance_cpu=attributes[0],
            performance_ram=attributes[1],
            performance_gpu=attributes[2],
            performance_disk=attributes[3],
            performance_network=attributes[4],
        )

        wrapper.session.add(work)
        wrapper.session.commit()

        return work
