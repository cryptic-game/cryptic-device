from app import wrapper, m
from schemes import requirement_build
from resources.game_content import check_compatible, calculate_power


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
