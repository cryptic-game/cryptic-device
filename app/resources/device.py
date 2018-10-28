from flask_restplus import Namespace, Resource, fields, abort
from basics import ErrorSchema, require_session
from objects import api
from typing import Optional
from models.device import DeviceModel


PublicDeviceResponseSchema = api.model("Public Device Response", {
    "uuid": fields.String(example="secretpassword1234",
                          description="the uuid/address"),
    "owner": fields.String(example="secretpassword1234",
                           description="the uuid/address"),
    "power": fields.Integer(example=3,
                            description="the device's power"),
    "powered_on": fields.Boolean(example=True,
                                 description="the device's power state")
})

PrivateDeviceResponseSchema = api.model("Public Device Response", {
    "uuid": fields.String(example="secretpassword1234",
                          description="the uuid/address"),
    "owner": fields.String(example="secretpassword1234",
                           description="the uuid/address"),
    "power": fields.Integer(example=3,
                            description="the device's power"),
    "powered_on": fields.Boolean(example=True,
                                 description="the device's power state")
})

device_api = Namespace('device')


@device_api.route('/public/<string:uuid>')
@device_api.doc("Public Device Application Programming Interface")
class PublicDeviceAPI(Resource):

    @device_api.doc("Information")
    @device_api.marshal_with(PublicDeviceResponseSchema)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @device_api.response(404, "Invalid Input", ErrorSchema)
    def get(self, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=uuid).first()

        if device is None:
            abort(404, "invalid device uuid")

        return device.serialize


@device_api.route('/private/<string:uuid>')
@device_api.doc("Private Device Application Programming Interface")
class PrivateDeviceAPI(Resource):

    @device_api.doc("Information")
    @device_api.marshal_with(PrivateDeviceResponseSchema)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @device_api.response(404, "Invalid Input", ErrorSchema)
    @require_session
    def get(self, session, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=uuid).first()

        if device is None:
            abort(404, "invalid device uuid")

        if session["owner"] != device.owner:
            abort(403, "no access on this device")

        return device.serialize
