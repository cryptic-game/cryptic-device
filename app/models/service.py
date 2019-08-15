from typing import Dict, Any, Union, Tuple

from sqlalchemy import Column, String, Float

from app import wrapper


class Service(wrapper.Base):
    """
    This is the service-requirements-model for cryptic-game
    """

    __tablename__: str = "device_service_req"

    service_uuid: Union[str, Column] = Column(String(36), primary_key=True, unique=True)
    device_uuid: Union[str, Column] = Column(String(36), nullable=False)

    allocated_cpu: Union[float, Column] = Column(Float)
    allocated_ram: Union[float, Column] = Column(Float)
    allocated_gpu: Union[float, Column] = Column(Float)
    allocated_disk: Union[float, Column] = Column(Float)
    allocated_network: Union[float, Column] = Column(Float)

    @property
    def serialize(self) -> Dict[str, Any]:
        _: str = self.service_uuid
        d = self.__dict__.copy()

        del d["_sa_instance_state"]

        return d

    @staticmethod
    def create(device: str, service: str, allocates: Tuple[float, float, float, float, float]) -> "Service":
        s: Service = Service(
            service_uuid=service,
            device_uuid=device,
            allocated_cpu=allocates[0],
            allocated_ram=allocates[1],
            allocated_gpu=allocates[2],
            allocated_disk=allocates[3],
            allocated_network=allocates[4],
        )

        wrapper.session.add(s)
        wrapper.session.commit()

        return s

    def export(self) -> Tuple[float, float, float, float, float]:
        return self.allocated_cpu, self.allocated_ram, self.allocated_gpu, self.allocated_disk, self.allocated_network

    def overwrite(self, data: Tuple[float, float, float, float, float]) -> None:
        self.allocated_cpu = data[0]
        self.allocated_ram = data[1]
        self.allocated_gpu = data[2]
        self.allocated_disk = data[3]
        self.allocated_network = data[4]
