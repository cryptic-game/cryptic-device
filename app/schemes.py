def make_error(*args: str, origin: str, sep: str = "") -> dict:
    return {"error": sep.join(map(str, args)), "origin": origin}


invalid_device_uuid: dict = make_error('invalid_device_uuid', origin='user')

invalid_file_uuid: dict = make_error('invalid_file_uuid', origin='user')

already_own_a_device: dict = make_error('already_own_a_device', origin='user')

permission_denied: dict = make_error('permission_denied', origin='user')

device_not_found: dict = make_error('device_not_found', origin='user')

file_not_found: dict = make_error('file_not_found', origin='user')

file_already_exists: dict = make_error('file_already_exists', origin='user')

success: dict = {'ok': True}
