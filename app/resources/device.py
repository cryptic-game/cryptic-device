from flask_restplus import Namespace, Resource, fields, abort
from basics import ErrorSchema, require_session, SuccessSchema
from objects import api
from typing import Optional
from models.device import DeviceModel
from objects import db
from sqlalchemy import func


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

PrivateDeleteDeviceResponseSchema = api.model("Public Delete Device Response", {
    "devices": fields.List(fields.Nested({
                    "uuid": fields.String,
                    "owner": fields.String,
                    "power": fields.Integer,
                    "powered_on": fields.Boolean,
                }), example="[{}, {}]",
                                 description="the uuid/address"),
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
    
    @device_api.doc("Ping")
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @device_api.response(404, "Invalid Input", ErrorSchema)
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

    @device_api.doc("Toggle")
    @device_api.marshal_with(PrivateDeviceResponseSchema)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @device_api.response(404, "Invalid Input", ErrorSchema)
    @require_session
    def post(self, session, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=uuid).first()

        if device is None:
            abort(404, "invalid device uuid")

        if session["owner"] != device.owner:
            abort(403, "no access on this device")

        device.powered_on = not device.powered_on
        db.session.commit()

        return device.serialize

    @device_api.doc("Delete")
    @device_api.marshal_with(SuccessSchema)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @device_api.response(404, "Invalid Input", ErrorSchema)
    @require_session
    def delete(self, session, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=uuid).first()

        if device is None:
            abort(404, "invalid device uuid")

        if session["owner"] != device.owner:
            abort(403, "no access on this device")

        db.session.delete(device)
        db.session.commit()

        return {"ok": True}


@device_api.route('/private')
@device_api.doc("Private Device Application Programming Interface for Modifications")
class PrivateDeviceModificationAPI(Resource):

    @device_api.doc("Information")
    @device_api.marshal_with(PrivateDeleteDeviceResponseSchema)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @device_api.response(404, "Invalid Input", ErrorSchema)
    @require_session
    def get(self, session):
        owner = session["owner"]
        all_devices = DeviceModel.query.filter_by(owner=owner).all()
       
        result = []

        for device in all_devices:
            result.append(device.serialize)
 
        return {
            "devices": result
        }

    @device_api.doc("Create")
    @device_api.marshal_with(SuccessSchema)
    @device_api.response(400, "Invalid Input", ErrorSchema)
    @device_api.response(404, "Invalid Input", ErrorSchema)
    @require_session
    def put(self, session):
        owner = session["owner"]
        all_devices = DeviceModel.query.filter_by(owner=owner).all()
        if len(all_devices) <= 0:
            device: Optional[DeviceModel] = DeviceModel.create(owner, 1, True)
        else:
            abort(400, "you already own one device")       
 
        return {"ok": True}

