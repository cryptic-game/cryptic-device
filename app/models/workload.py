from typing import Dict, Any, Union, Tuple

from sqlalchemy import Column, String, Float

from app import wrapper


class Workload(wrapper.Base):
    """
    This is the workload-model for cryptic-game
    """

    __tablename__: str = "device_workload"

    uuid: Union[Column, str] = Column(String(36), primary_key=True, unique=True)

    performance_cpu: Union[float, Column] = Column(Float, nullable=False)
    performance_gpu: Union[float, Column] = Column(Float, nullable=False)
    performance_ram: Union[float, Column] = Column(Float, nullable=False)
    performance_disk: Union[float, Column] = Column(Float, nullable=False)
    performance_network: Union[float, Column] = Column(Float, nullable=False)

    usage_cpu: Union[float, Column] = Column(Float)
    usage_gpu: Union[float, Column] = Column(Float)
    usage_ram: Union[float, Column] = Column(Float)
    usage_disk: Union[float, Column] = Column(Float)
    usage_network: Union[float, Column] = Column(Float)

    @property
    def serialize(self) -> Dict[str, Any]:
        _: str = self.uuid
        d = self.__dict__.copy()

        del d["_sa_instance_state"]

        return d

    @staticmethod
    def create(device: str, attributes: Tuple[float, float, float, float, float]) -> "Workload":
        work: Workload = Workload(
            uuid=device,
            performance_cpu=attributes[0],
            performance_ram=attributes[1],
            performance_gpu=attributes[2],
            performance_disk=attributes[3],
            performance_network=attributes[4],
            usage_cpu=0,
            usage_gpu=0,
            usage_ram=0,
            usage_disk=0,
            usage_network=0,
        )

        wrapper.session.add(work)
        wrapper.session.commit()

        return work

    def service(self, new_service: Tuple[float, float, float, float, float]):
        self.usage_cpu += new_service[0]
        self.usage_ram += new_service[1]
        self.usage_gpu += new_service[2]
        self.usage_disk += new_service[3]
        self.usage_network += new_service[4]
        wrapper.session.commit()

    def workload_notification(self, origin: str) -> dict:
        return {
            "notify-id": "resource-usage",
            "origin": origin,
            "device_uuid": self.uuid,
            "data": self.display()
        }

    def display(self) -> dict:
        return {
            "cpu": min(self.usage_cpu / self.performance_cpu, 1),
            "ram": min(self.usage_ram / self.performance_ram, 1),
            "gpu": min(self.usage_gpu / self.performance_gpu, 1),
            "disk": min(self.usage_disk / self.performance_disk, 1),
            "network": min(self.usage_network / self.performance_network, 1),
        }
