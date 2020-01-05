from scheme import Text, Sequence, UUID

from models.file import CONTENT_LENGTH


def make_error(*args: str, origin: str, sep: str = "") -> dict:
    return {"error": sep.join(map(str, args)), "origin": origin}


already_own_a_device: dict = make_error("already_own_a_device", origin="user")

maximum_devices_reached: dict = make_error("maximum_devices_reached", origin="user")

permission_denied: dict = make_error("permission_denied", origin="user")

device_not_found: dict = make_error("device_not_found", origin="user")

device_powered_off: dict = make_error("device_powered_off", origin="user")

file_not_found: dict = make_error("file_not_found", origin="user")

file_already_exists: dict = make_error("file_already_exists", origin="user")

service_not_found: dict = make_error("service_not_found", origin="service")

service_already_running: dict = make_error("service_already_running", origin="service")

service_not_running: dict = make_error("service_not_running", origin="service")

success: dict = {"ok": True}

requirement_device: dict = {"device_uuid": UUID()}

requirement_change_name: dict = {"device_uuid": UUID(), "name": Text(min_length=1, max_length=15)}

requirement_build: dict = {
    "gpu": Sequence(Text(nonempty=True)),
    "cpu": Sequence(Text(nonempty=True)),
    "mainboard": Text(nonempty=True),
    "ram": Sequence(Text(nonempty=True)),
    "disk": Sequence(Text(nonempty=True)),
    "processorCooler": Sequence(Text(nonempty=True)),
    "powerPack": Text(nonempty=True),
    "case": Text(nonempty=True),
}

requirement_file: dict = {"device_uuid": UUID(), "file_uuid": UUID()}

requirement_file_move: dict = {
    "device_uuid": UUID(),
    "file_uuid": UUID(),
    "filename": Text(min_length=1, max_length=64),
}

requirement_file_update: dict = {"device_uuid": UUID(), "file_uuid": UUID(), "content": Text(max_length=CONTENT_LENGTH)}

requirement_file_create: dict = {
    "device_uuid": UUID(),
    "filename": Text(min_length=1, max_length=64),
    "content": Text(max_length=CONTENT_LENGTH),
}

requirement_service: dict = {"service_uuid": UUID()}
