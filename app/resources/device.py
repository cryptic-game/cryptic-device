from flask_restplus import Namespace, Resource, fields, abort
from basics import ErrorSchema, require_session, SuccessSchema
from objects import api
from flask import request
from typing import Optional, List
from models.device import DeviceModel
from objects import db
from sqlalchemy import func

PublicDeviceResponseSchema = api.model("Public Device Response", {
    "uuid": fields.String(example="secretpassword1234",
                          description="the uuid/address"),
    "name": fields.String(example="asterix",
                          description="the name/alias"),
    "owner": fields.String(example="secretpassword1234",
                           description="the uuid/address"),
    "power": fields.Integer(example=3,
                            description="the device's power"),
    "powered_on": fields.Boolean(example=True,
                                 description="the device's power state")
})

PublicDevicePingResponseSchema = api.model("Public Device Ping Response", {
    "online": fields.Boolean(example=True,
                             description="the device's online status")
})

PrivateChangeNameDeviceRequestSchema = api.model("Public Delete Device Response", {
    "name": fields.String(example="obelix",
                          description="the name to change on the device")
})

PrivateDeviceResponseSchema = api.model("Public Device Response", {
    "uuid": fields.String(example="secretpassword1234",
                          description="the uuid/address"),
    "name": fields.String(example="asterix",
                          description="the name/alias"),
    "owner": fields.String(example="secretpassword1234",
                           description="the uuid/address"),
    "power": fields.Integer(example=3,
                            description="the device's power"),
    "powered_on": fields.Boolean(example=True,
                                 description="the device's power state")
})

PrivateDevicesResponseSchema = api.model("Public Delete Device Response", {
    "devices": fields.List(fields.Nested(PrivateDeviceResponseSchema),
                           example="[{}, {}]",
                           description="the uuid/address")
})

device_api = Namespace('device')


@device_api.route('/public/<string:uuid>')
@device_api.doc("Public Device Application Programming Interface")
class PublicDeviceAPI(Resource):

    @device_api.doc("Get public information about a device")
    @device_api.marshal_with(PublicDeviceResponseSchema)
    @device_api.response(404, "Not Found", ErrorSchema)
    def get(self, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=uuid).first()

        if device is None:
            abort(404, "invalid device uuid")

        return device.serialize

    @device_api.doc("Ping a device")
    @device_api.marshal_with(PublicDevicePingResponseSchema)
    @device_api.response(404, "Not Found", ErrorSchema)
    def post(self, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=uuid).first()

        if device is None:
            abort(404, "invalid device uuid")

        return {
            "online": device.powered_on
        }


@device_api.route('/private/<string:uuid>')
@device_api.doc("Private Device Application Programming Interface")
class PrivateDeviceAPI(Resource):

    @device_api.doc("Get private information about the device")
    @device_api.marshal_with(PrivateDeviceResponseSchema)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @device_api.response(403, "No Access", ErrorSchema)
    @device_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def get(self, session, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=uuid).first()

        if device is None:
            abort(404, "invalid device uuid")

        if session["owner"] != device.owner:
            abort(403, "no access to this device")

        return device.serialize

    @device_api.doc("Turn the device on/off")
    @device_api.marshal_with(PrivateDeviceResponseSchema)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @device_api.response(403, "No Access", ErrorSchema)
    @device_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def post(self, session, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=uuid).first()

        if device is None:
            abort(404, "invalid device uuid")

        if session["owner"] != device.owner:
            abort(403, "no access to this device")

        device.powered_on = not device.powered_on
        db.session.commit()

        return device.serialize

    @device_api.doc("Change name of device")
    @device_api.marshal_with(PrivateDeviceResponseSchema)
    @device_api.expect(PrivateChangeNameDeviceRequestSchema, validate=True)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @device_api.response(403, "No Access", ErrorSchema)
    @device_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def put(self, session, uuid):
        name = request.json["name"]

        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=uuid).first()

        if device is None:
            abort(404, "invalid device uuid")

        if session["owner"] != device.owner:
            abort(403, "no access to this device")

        device.name = name
        db.session.commit()

        return device.serialize

    @device_api.doc("Delete a device")
    @device_api.marshal_with(SuccessSchema)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @device_api.response(404, "No Access", ErrorSchema)
    @device_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def delete(self, session, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=uuid).first()

        if device is None:
            abort(404, "invalid device uuid")

        if session["owner"] != device.owner:
            abort(403, "no access to this device")

        db.session.delete(device)
        db.session.commit()

        return {"ok": True}


@device_api.route('/private')
@device_api.doc("Private Device Application Programming Interface for Modifications")
class PrivateDeviceModificationAPI(Resource):

    @device_api.doc("Get all devices")
    @device_api.marshal_with(PrivateDevicesResponseSchema, as_list=True)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @require_session
    def get(self, session):
        devices: List[DeviceModel] = DeviceModel.query.filter_by(owner=session["owner"]).all()

        return {
            "devices": [e.serialize for e in devices]
        }

    @device_api.doc("Create a device")
    @device_api.marshal_with(PrivateDeviceResponseSchema)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @require_session
    def put(self, session):
        owner: str = session["owner"]

        device_count: int = \
            (db.session.query(func.count(DeviceModel.uuid)).filter(DeviceModel.owner == owner)).first()[0]

        if device_count != 0:
            abort(400, "you already own a device")

        device: DeviceModel = DeviceModel.create(owner, 1, True)

        return device.serialize
