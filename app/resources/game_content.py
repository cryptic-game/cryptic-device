import math
from typing import Tuple, List

from app import m, wrapper
from models.hardware import Hardware
from models.service import Service
from models.workload import Workload
from models.file import File
from vars import hardware


def check_exists(user: str, elements: dict) -> Tuple[bool, dict]:
    response: dict = m.contact_microservice("inventory", ["inventory", "list"], {"owner": user})

    names: List[str] = [x["element_name"] for x in response["elements"]]

    for element_type in ("mainboard", "powerPack", "case"):
        if elements[element_type] not in names:
            return False, {"error": f"{element_type}_not_in_inventory"}
    for element_type in ("cpu", "gpu", "processorCooler", "disk", "ram"):
        for element in elements[element_type]:
            if element not in names:
                return False, {"error": f"{element_type}_not_in_inventory"}
            else:
                names.remove(element)

    return True, {}


def delete_items(user: str, elements: dict):
    for element_type in ("mainboard", "powerPack", "case"):
        m.contact_microservice(
            "inventory", ["inventory", "delete_by_name"], {"owner": user, "item_name": elements[element_type]}
        )
    for element_type in ("cpu", "gpu", "processorCooler", "disk", "ram"):
        for element in elements[element_type]:
            m.contact_microservice("inventory", ["inventory", "delete_by_name"], {"owner": user, "item_name": element})


def check_element_existence(elements: dict) -> Tuple[bool, dict]:
    for element_type in ("mainboard", "powerPack", "case"):
        if elements[element_type] not in hardware[element_type]:
            return False, {"error": f"element_{element_type}_not_found"}
    for element_type in ("cpu", "gpu", "processorCooler", "disk", "ram"):
        for element in elements[element_type]:
            if element not in hardware[element_type]:
                return False, {"error": f"element_{element_type}_not_found"}

    return True, {}


def check_compatible(elements: dict) -> Tuple[bool, dict]:
    exists, message = check_element_existence(elements)
    if not exists:
        return False, message

    cpu_units: List[str] = elements["cpu"]
    mainboard: str = elements["mainboard"]
    gpu_units: List[str] = elements["gpu"]
    disk_units: List[str] = elements["disk"]
    ram_units: List[str] = elements["ram"]
    cooler_units: List[str] = elements["processorCooler"]
    power_pack: str = elements["powerPack"]
    case: str = elements["case"]

    if not cpu_units:
        return False, {"error": "missing_cpu"}
    if not ram_units:
        return False, {"error": "missing_ram"}
    if not disk_units:
        return False, {"error": "missing_disk"}
    if len(cpu_units) != len(cooler_units):
        return False, {"error": "invalid_amount_of_cpu_coolers"}

    # Case
    if case != hardware["mainboard"][mainboard]["case"]:
        return False, {"error": "incompatible_case"}

    external_gpu_necessary = hardware["mainboard"][mainboard]["graphicUnitOnBoard"] is None
    total_power = hardware["mainboard"][mainboard]["power"]

    # CPU and coolers
    if len(cpu_units) > hardware["mainboard"][mainboard]["cpuSlots"]:
        return False, {"error": "not_enough_cpu_slots"}

    for cpu, cooler in zip(cpu_units, cooler_units):
        if hardware["cpu"][cpu]["socket"] != hardware["mainboard"][mainboard]["cpuSocket"]:
            return False, {"error": "incompatible_cpu_socket"}
        if hardware["cpu"][cpu]["socket"] != hardware["processorCooler"][cooler]["socket"]:
            return False, {"error": "incompatible_cooler_socket"}

        if hardware["cpu"][cpu]["graphicUnit"] is not None:
            external_gpu_necessary = False

        total_power += hardware["cpu"][cpu]["power"] + hardware["processorCooler"][cooler]["power"]

    # external GPU
    if external_gpu_necessary and not gpu_units:
        return False, {"error": "missing_external_gpu"}

    expansion_slots = {
        slot["interface"]: slot["interfaceSlots"] for slot in hardware["mainboard"][mainboard]["expansionSlots"]
    }
    for gpu in gpu_units:
        interface = hardware["gpu"][gpu]["interface"]
        if interface not in expansion_slots or expansion_slots[interface] <= 0:
            return False, {"error": "no_compatible_expansion_slot_for_gpu"}
        expansion_slots[interface] -= 1

        total_power += hardware["gpu"][gpu]["power"]

    # Disks
    remaining_disk_slots = hardware["mainboard"][mainboard]["diskStorage"]["diskSlots"]
    for disk in disk_units:
        total_power += hardware["disk"][disk]["power"]

        interface = hardware["disk"][disk]["interface"]
        if interface in expansion_slots and expansion_slots[interface] >= 1:
            expansion_slots[interface] -= 1
            continue

        if remaining_disk_slots <= 0 or interface not in hardware["mainboard"][mainboard]["diskStorage"]["interface"]:
            return False, {"error": "no_compatible_expansion_slot_for_disk"}
        remaining_disk_slots -= 1

    # RAM
    if len(ram_units) > hardware["mainboard"][mainboard]["ram"]["ramSlots"]:
        return False, {"error": "not_enough_ram_slots"}

    total_ram_size = 0
    for ram in ram_units:
        total_power += hardware["ram"][ram]["power"]

        total_ram_size += hardware["ram"][ram]["ramSize"]

        if hardware["ram"][ram]["ramTyp"] not in hardware["mainboard"][mainboard]["ram"]["ramTyp"]:
            return False, {"error": "incompatible_ram_type"}
        if hardware["ram"][ram]["frequency"] not in hardware["mainboard"][mainboard]["ram"]["frequency"]:
            return False, {"error": "incompatible_ram_frequency"}

    if total_ram_size > hardware["mainboard"][mainboard]["ram"]["maxRamSize"]:
        return False, {"error": "ram_limit_exceeded"}

    # PowerPack
    if total_power > hardware["powerPack"][power_pack]["totalPower"]:
        return False, {"error": "insufficient_power_pack"}

    return True, {}


def calculate_power(elements: dict) -> Tuple[float, float, float, float, float]:
    cpu_units: List[str] = elements["cpu"]
    mainboard: str = elements["mainboard"]
    gpu_units: List[str] = elements["gpu"]
    disk_units: List[str] = elements["disk"]
    ram_units: List[str] = elements["ram"]

    performance_cpu: float = sum(
        hardware["cpu"][cpu]["cores"] * hardware["cpu"][cpu]["frequencyMax"] for cpu in cpu_units
    )

    performance_ram: float = sum(
        hardware["ram"][ram]["ramTyp"][1]
        * math.sqrt(hardware["ram"][ram]["ramSize"] * hardware["ram"][ram]["frequency"])
        for ram in ram_units
    )

    def calc_gpu_performance(gpu: dict) -> float:
        if gpu is None:
            return 0

        if "ramTyp" in gpu:
            ram_type: float = gpu["ramTyp"][1]
        else:
            ram_type: float = 1
        return ram_type * math.sqrt(gpu["frequency"] * gpu["ramSize"])

    performance_gpu: float = max(
        map(
            calc_gpu_performance,
            [hardware["mainboard"][mainboard]["graphicUnitOnBoard"]]
            + [hardware["cpu"][cpu]["graphicUnit"] for cpu in cpu_units]
            + [hardware["gpu"][gpu] for gpu in gpu_units],
        )
    )

    disk_speed: float = sum(
        100 * math.log10(hardware["disk"][disk]["writingSpeed"] * hardware["disk"][disk]["readingSpeed"])
        for disk in disk_units
    )

    network: float = hardware["mainboard"][mainboard]["networkPort"]["speed"]

    return performance_cpu, performance_ram, performance_gpu, disk_speed, network


def create_hardware(elements: dict, device_uuid: str) -> None:
    for element_type in ("mainboard", "powerPack", "case"):
        Hardware.create(device_uuid, elements[element_type], element_type)
    for element_type in ("cpu", "gpu", "processorCooler", "disk", "ram"):
        for element in elements[element_type]:
            Hardware.create(device_uuid, element, element_type)


def scale_resources(s: List[Service], scale: Tuple[float, float, float, float, float]):
    for service in s:
        send: dict = {
            "service_uuid": service.service_uuid,
            "cpu": scale[0] * service.allocated_cpu,
            "ram": scale[1] * service.allocated_ram,
            "gpu": scale[2] * service.allocated_gpu,
            "disk": scale[3] * service.allocated_disk,
            "network": scale[4] * service.allocated_network,
        }

        m.contact_microservice("service", ["hardware", "scale"], send)


def generate_scale(
    data: Tuple[float, float, float, float, float], wl: Workload
) -> Tuple[float, float, float, float, float]:
    return (
        wl.performance_cpu / (wl.usage_cpu + data[0]) if wl.usage_cpu + data[0] > wl.performance_cpu else 1.0,
        wl.performance_ram / (wl.usage_ram + data[1]) if wl.usage_ram + data[1] > wl.performance_ram else 1.0,
        wl.performance_gpu / (wl.usage_gpu + data[2]) if wl.usage_gpu + data[2] > wl.performance_gpu else 1.0,
        wl.performance_disk / (wl.usage_disk + data[3]) if wl.usage_disk + data[3] > wl.performance_disk else 1.0,
        wl.performance_network / (wl.usage_network + data[4])
        if wl.usage_network + data[4] > wl.performance_network
        else 1.0,
    )


def dict2tuple(data: dict) -> Tuple[float, float, float, float, float]:
    return data["cpu"], data["ram"], data["gpu"], data["disk"], data["network"]


def turn(data: Tuple[float, float, float, float, float]) -> Tuple[float, float, float, float, float]:
    return -1 * data[0], -1 * data[1], -1 * data[2], -1 * data[3], -1 * data[4]


def stop_all_service(device_uuid: str, delete: bool = False) -> None:
    for obj in wrapper.session.query(Service).filter_by(device_uuid=device_uuid).all():
        wrapper.session.delete(obj)
    wl: Workload = wrapper.session.query(Workload).get(device_uuid)
    wl.usage_cpu = 0
    wl.usage_ram = 0
    wl.usage_gpu = 0
    wl.usage_disk = 0
    wl.usage_network = 0
    if delete:
        wrapper.session.delete(wl)
    wrapper.session.commit()


def stop_services(device_uuid: str) -> None:
    m.contact_microservice("service", ["hardware", "stop"], {"device_uuid": device_uuid})


def delete_services(device_uuid: str) -> None:
    m.contact_microservice("service", ["hardware", "delete"], {"device_uuid": device_uuid})


def delete_files(device_uuid: str) -> None:
    files: list = wrapper.session.query(File).filter_by(device=device_uuid)
    for file in files:
        wrapper.session.delete(file)


def generate_scale_with_no_new(wl: Workload) -> Tuple[float, float, float, float, float]:
    return (
        wl.performance_cpu / wl.usage_cpu if wl.usage_cpu > wl.performance_cpu else 1.0,
        wl.performance_ram / wl.usage_ram if wl.usage_ram > wl.performance_ram else 1.0,
        wl.performance_gpu / wl.usage_gpu if wl.usage_gpu > wl.performance_gpu else 1.0,
        wl.performance_disk / wl.usage_disk if wl.usage_disk > wl.performance_disk else 1.0,
        wl.performance_network / wl.usage_network if wl.usage_network > wl.performance_network else 1.0,
    )


def calculate_real_use(service_uuid: str) -> dict:
    service: Service = wrapper.session.query(Service).get(service_uuid)

    wl: Workload = wrapper.session.query(Workload).get(service.device_uuid)

    scales: Tuple[float, float, float, float, float] = generate_scale_with_no_new(wl)

    return {
        "cpu": scales[0] * service.allocated_cpu,
        "ram": scales[1] * service.allocated_gpu,
        "gpu": scales[2] * service.allocated_ram,
        "disk": scales[3] * service.allocated_disk,
        "network": scales[4] * service.allocated_network,
    }
