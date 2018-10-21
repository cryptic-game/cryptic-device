from flask import Blueprint, request, Response
from util import make_response

info = Blueprint('info', __name__)


@info.route("/", methods=["GET"])
def information() -> Response:
    """
    Returns the current session informations by the auth-token

    :return: The current session with informations of owner
    """

    return make_response({
    	"status": "ok"
    })
