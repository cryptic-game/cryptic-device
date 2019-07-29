from app import wrapper, m
from schemes import requirement_build, device_not_found
from resources.game_content import check_compatible, calculate_power, scale_resources, generate_scale, dict2tuple, turn
from scheme import UUID
from models.workload import Workload
from models.service import Service
from models.device import Device
from typing import List, Tuple


@m.user_endpoint(path=["hardware", "build"], requires=requirement_build)
def build(data: dict, user: str):
    """
    This endpoint you can test your build if the parts a compatible and what is required for a device
    """
    comp, message = check_compatible(data)
    if not comp:
        return message

    performance: tuple = calculate_power(data)

    return_message: dict = {"success": True, "performance": performance}

    return return_message


@m.user_endpoint(path=["hardware", "resources"], requires={"device_uuid": UUID()})
def hardware_resources(data: dict, user: str):
    wl: Workload = wrapper.session.query(Workload).get(data["device_uuid"])

    if wl is None:
        return device_not_found

    return wl.display()


@m.microservice_endpoint(path=["hardware", "register"])
def hardware_register(data: dict, microservice: str):
    # cpu_requirements, ram_req, gpu_req, disk_req, network_req

    wl: Workload = wrapper.session.query(Workload).get(data["device_uuid"])

    if wl is None:
        return device_not_found

    ser: Service = wrapper.session.query(Service).get(data["service_uuid"])

    if ser is not None:
        return {"error": "Service already running"}

    other: List[Service] = wrapper.session.query(Service).filter_by(device_uuid=data["device_uuid"]).all()

    new: Tuple[float, float, float, float, float] = dict2tuple(data)

    scales: Tuple[float, float, float, float, float] = generate_scale(new, wl)

    scale_resources(other, scales)

    wl.service(new)

    ser: Service = Service.create(data["device_uuid"], data["service_uuid"], new)

    return_value: dict = {
        "service_uuid": ser.service_uuid,
        "cpu": ser.allocated_cpu * scales[0],
        "ram": ser.allocated_ram * scales[1],
        "gpu": ser.allocated_gpu * scales[2],
        "disk": ser.allocated_disk * scales[3],
        "network": ser.allocated_network * scales[4],
    }

    m.contact_user(data["user"], wl.display())

    return return_value


@m.microservice_endpoint(path=["hardware", "stop"])
def hardware_stop(data: dict, microservice: str):
    ser: Service = wrapper.session.query(Service).get(data["service_uuid"])
    if ser is None:
        return {"error": "service_is_not_running"}

    wl: Workload = wrapper.session.query(Workload).get(data["device_uuid"]).first()
    if wl is None:
        return device_not_found

    attributes: Tuple[float, float, float, float, float] = turn(ser.export())

    wrapper.session.delete(ser)
    wrapper.session.commit()

    wl.service(attributes)
    new_scales: Tuple[float, float, float, float, float] = generate_scale(attributes, wl)

    other: List[Service] = wrapper.session.query(Service).filter_by(device_uuid=data["device_uuid"]).all()
    scale_resources(other, new_scales)

    m.contact_user(data["user"], wl.display())

    return {"ok": True}
