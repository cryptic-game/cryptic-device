from scheme import Text, Sequence


def make_error(*args: str, origin: str, sep: str = "") -> dict:
    return {"error": sep.join(map(str, args)), "origin": origin}


already_own_a_device: dict = make_error("already_own_a_device", origin="user")

permission_denied: dict = make_error("permission_denied", origin="user")

device_not_found: dict = make_error("device_not_found", origin="user")

file_not_found: dict = make_error("file_not_found", origin="user")

file_already_exists: dict = make_error("file_already_exists", origin="user")

service_not_found: dict = make_error("service_not_found", origin="service")

success: dict = {"ok": True}

requirement_build: dict = {
    "gpu": Text(),
    "cpu": Text(),
    "motherboard": Text(),
    "ram": Sequence(Text(nonempty=True)),
    "disk": Sequence(Text(nonempty=True)),
}
