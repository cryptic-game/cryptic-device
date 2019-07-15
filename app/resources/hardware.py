from app import wrapper, m


@m.user_endpoint(path=["hardware", "build"])
def build(data: dict, user: str):
    """
    This endpoint you can test your build if the parts a compatible and what is required for a device
    """
    return {}
