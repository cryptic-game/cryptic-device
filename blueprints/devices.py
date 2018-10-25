from flask import Blueprint, request, Response
from util import make_response
from models.device import Device

devices = Blueprint('devices', __name__)


@devices.route("/<address>/information", methods=["GET"])
def information(address) -> Response:
    """
    Returns public information about the specified device
    """

    # TODO Activate auth when API is finished
    #token = request.headers.get('Token')
    #session = Session.find(token)
    #if session is None:
    #    return make_response({
    #        "error": "token does not exists"
    #    })
    #return make_response({
    #    "session": session.as_simple_dict(),
    #    "user": User.get_by_id(session.owner).as_private_simple_dict()
    #})

    dev = Device.get_by_address(address)

    if not dev:
        return make_response({"error": "device does not exists"})
    
    return make_response(dev.as_public_simple_dict())
