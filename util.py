import json
import typing
from flask import Response


def make_response(data: typing.Any) -> Response:
    """
    Creates a response object.

    :param data: Json object to be returned
    :return: A response object with body and mimetype set.
    """
    return Response(json.dumps(data), mimetype='application/json')