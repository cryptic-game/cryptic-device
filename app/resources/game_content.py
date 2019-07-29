from vars import hardware, resolve_ram_type, resolve_gpu_type
from typing import Tuple, List
import math
from models.hardware import Hardware
from models.device import Device
from models.service import Service
from models.workload import Workload
from app import m


def check_exists(user: str, elements: dict) -> Tuple[bool, dict]:
    response: dict = m.contact_microservice("inventory", ["inventory", "list"], {"owner": user})

    names: List[str] = [x["element_name"] for x in response["elements"]]

    if elements["cpu"] not in names:
        return (False, {"error": "you_dont_own_such_cpu"})
    if elements["motherboard"] not in names:
        return (False, {"error": "you_dont_own_such_motherboard"})
    if elements["gpu"] not in names:
        return (False, {"error": "you_dont_own_such_gpu"})
    for ram in elements["ram"]:
        if ram not in names:
            return (False, {"error": "you_dont_own_such_ram"})
        else:
            names.remove(ram)
    for disk in elements["disk"]:
        if disk not in names:
            return (False, {"error": "you_dont_own_such_disk"})
        else:
            names.remove(disk)

    return (True, {})


def delete(user: str, elements: dict):
    m.contact_microservice("inventory", ["inventory", "delete_by_name"], {"user": user, "name": elements["cpu"]})
    m.contact_microservice(
        "inventory", ["inventory", "delete_by_name"], {"user": user, "name": elements["motherboard"]}
    )
    m.contact_microservice("inventory", ["inventory", "delete_by_name"], {"user": user, "name": elements["gpu"]})
    for ram in elements["ram"]:
        m.contact_microservice("inventory", ["inventory", "delete_by_name"], {"user": user, "name": ram})
    for disk in elements["disk"]:
        m.contact_microservice("inventory", ["inventory", "delete_by_name"], {"user": user, "name": disk})


def check_element_existens(elements: dict) -> Tuple[bool, dict]:

    if not elements["cpu"] in hardware["cpu"].key():
        return (False, {"error": "element_cpu_not_found"})
    if not elements["gpu"] in hardware["gpu"].keys():
        return (False, {"error": "element_gpu_not_found"})
    if not elements["motherboard"] in hardware["mainboards"].keys():
        return (False, {"error": "element_motherboard_not_found"})
    for disk in elements["disk"]:
        if not disk in hardware["diskStorage"].keys():
            return (False, {"error": "element_disk_not_found"})
    for ram in elements["ram"]:
        if not ram in hardware["ram"].keys():
            return (False, {"error": "element_ram_not_found"})

    return (True, {})


def check_compatible(elements: dict) -> Tuple[bool, dict]:

    exists, message = check_element_existens(elements)
    if not exists:
        return (False, message)

    cpu: str = elements["cpu"]
    motherboard: str = elements["motherboard"]
    ram: List[str] = elements["ram"]
    gpu: str = elements["gpu"]
    disk: List[str] = elements["disk"]

    if hardware["cpu"][cpu]["sockel"] != hardware["mainboards"][motherboard]["sockel"]:
        return (False, {"error": "cpu_and_mainboard_sockel_do_not_fit"})

    if hardware["mainboards"][motherboard]["ram"]["ramSlots"] < len(ram):
        return (False, {"error": "mainboard_has_not_this_many_ram_slots"})

    for ram_stick in ram:
        if hardware["ram"][ram_stick]["ramTyp"] != hardware["mainboards"][motherboard]["ram"]["typ"]:
            return (False, {"error": "ram_type_does_not_fit_what_you_have_on_your_mainboard"})

    for i in disk:
        if hardware["diskStorage"][i]["interface"] != hardware["mainboards"][motherboard]["diskStorage"]["interface"]:
            return (False, {"error": "your_hard_drive_interface_does_not_fit_with_the_motherboards_one"})

    return (True, {})


def calculate_power(elements: dict) -> Tuple[float, float, float, float, float]:

    cpu: str = elements["cpu"]
    motherboard: str = elements["motherboard"]
    ram: List[str] = elements["ram"]
    gpu: str = elements["gpu"]
    disk: List[str] = elements["disk"]

    performance_cpu: float = hardware["cpu"][cpu]["cores"] * hardware["cpu"][cpu]["frequencyMax"]

    performance_ram: float = 1
    for ram_stick in ram:
        performance_ram += (
            min(
                resolve_ram_type[hardware["mainboards"][motherboard]["ram"]["type"]],
                resolve_ram_type[hardware["ram"][ram_stick]["ramTyp"]],
            )
            * hardware["ram"][ram_stick]["ramsize"]
        )

    performance_gpu: float = resolve_gpu_type[hardware["graphiccards"][gpu]["interface"]] * math.sqrt(
        hardware["graphiccard"][gpu]["ramsize"] * hardware["graphiccard"][gpu]["frequency"]
    )

    dick_storage: float = 1

    for i in disk:
        dick_storage += hardware["diskStorage"][i]["capacity"] * math.log1p(
            hardware["diskStorage"][i]["writingSpeed"] * hardware["diskStorage"][i]["readingSpeed"]
        )

    network: float = hardware["mainboards"][motherboard]["speed"]

    return (performance_cpu, performance_ram, performance_gpu, dick_storage, network)


def add_able(elements: dict, type_new: str) -> bool:

    if type_new == "cpu" and "cpu" in elements.keys():
        return False
    if type_new == "motherboard" and "motherboard" in elements.keys():
        return False
    if type_new == "gpu" and "gpu" in elements.keys():
        return False
    if type_new == "harddrive":
        # TODO check for multiple harddrives dependinng on spaces in the motherboard
        pass

    return True


def create_hardware(elements: dict, device_uuid: str) -> None:

    Hardware.create(device_uuid, elements["cpu"], "cpu")
    Hardware.create(device_uuid, elements["gpu"], "gpu")
    Hardware.create(device_uuid, elements["motherboard"], "mainboard")
    for disk in elements["disk"]:
        Hardware.create(device_uuid, disk, "diskStorage")
    for ram in elements["ram"]:
        Hardware.create(device_uuid, ram, "ram")


def scale_resources(s: List[Service], scale: Tuple[float, float, float, float, float]):

    for service in s:
        send: dict = {}
        send["service_uuid"] = service.service_uuid
        send["cpu"] = scale[0] * service.allocated_cpu
        send["ram"] = scale[1] * service.allocated_raml
        send["gpu"] = scale[2] * service.allocated_gpu
        send["disk"] = scale[3] * service.allocated_disk
        send["network"] = scale[4] * service.allocated_network

        m.contact_microservice("service", ["hardware", "scale"], send)


def generate_scale(
    data: Tuple[float, float, float, float, float], wl: Workload
) -> Tuple[float, float, float, float, float]:

    if wl.usage_cpu + data[0] < wl.performance_cpu:
        cpu: float = 1
    else:
        scale: float = (1 - (wl.usage_cpu + data[0] - wl.performance_cpu)) / (wl.usage_cpu + data[0])
        cpu: float = scale

    if wl.usage_ram + data[1] < wl.performance_ram:
        ram: float = 1
    else:
        scale: float = (1 - (wl.usage_ram + data[1] - wl.performance_ram)) / (wl.usage_cpu + data[1])
        ram: float = scale
    if wl.usage_gpu + data[2] > wl.performance_gpu:
        gpu: float = 1
    else:
        scale: float = (1 - (wl.usage_gpu + data[2] - wl.performance_gpu)) / (wl.usage_cpu + data[2])
        gpu: float = scale
    if wl.usage_disk + data[3] > wl.performance_disk:
        disk: float = 1
    else:
        scale: float = (1 - (wl.usage_disk + data[3] - wl.performance_disk)) / (wl.usage_disk + data[3])
        disk: float = scale
    if wl.usage_network + data[4] > wl.performance_network:
        network: float = 1
    else:
        scale: float = (1 - (wl.usage_network + data[4] - wl.performance_network)) / (wl.usage_network + data[4])
        network: float = scale
    return (cpu, ram, gpu, disk, network)


def dict2tuple(data: dict) -> Tuple[float, float, float, float, float]:
    return (data["cpu"], data["ram"], data["gpu"], data["disk"], data["network"])


def turn(data: Tuple[float, float, float, float, float]) -> Tuple[float, float, float, float, float]:
    return (-1 * data[0], -1 * data[1], -1 * data[2], -1 * data[3], -1 * data[4])
