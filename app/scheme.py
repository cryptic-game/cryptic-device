def make_error(*args: str, origin: str, sep: str = "") -> dict:
    return {"error": sep.join(map(str, args)), "origin": origin}


invalid_device: dict = make_error('invalid device uuid', origin='user')

invalid_file: dict = make_error('invalid file uuid', origin='user')

alread_have_device: dict = make_error('you already own a device', origin='user')

permission_denied: dict = make_error('no access to this device', origin='user')

no_name: dict = make_error('no name given', origin='user')

this_device_does_not_exists: dict = make_error("this device does not exists", origin='user')

no_content: dict = make_error('no content given', origin='user')

no_file_name: dict = make_error('no filename given', origin='user')

length_exceeded: dict = make_error('file length exceeded', origin='user')

no_file: dict = make_error('no file with this name exist', origin='user')

file_already_exists: dict = make_error('filename already taken', origin='user')

success: dict = {'ok': True}
