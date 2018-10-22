from flask import Blueprint, request, Response
from util import make_response
from models.device import Device

info = Blueprint('info', __name__)


@info.route("/", methods=["GET"])
def information() -> Response:
    """
    Returns data about the target device
    """

    # TODO check here the target device

    return make_response({
    	"status": "ok"
    })
