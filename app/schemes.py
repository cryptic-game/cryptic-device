def make_error(*args: str, origin: str, sep: str = "") -> dict:
    return {"error": sep.join(map(str, args)), "origin": origin}


invalid_device: dict = make_error('invalid_device_uuid', origin='user')

invalid_file: dict = make_error('invalid_file_uuid', origin='user')

already_have_device: dict = make_error('already_owns_a_device', origin='user')

permission_denied: dict = make_error('permission_denied', origin='user')

this_device_does_not_exists: dict = make_error('device_does_not_exists', origin='user')

no_file: dict = make_error('file_does_not_exist', origin='user')

file_already_exists: dict = make_error('file_already_exists', origin='user')

success: dict = {'ok': True}
