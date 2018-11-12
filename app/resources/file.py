from flask_restplus import Namespace, Resource, fields, abort
from basics import ErrorSchema, require_session, SuccessSchema
from objects import api
from flask import request
from models.file import FileModel, CONTENT_LENGTH
from models.device import DeviceModel
from objects import db
from sqlalchemy import func
from typing import Optional

FileResponseSchema = api.model("File Response", {
    "uuid": fields.String(example="12abc34d5efg67hi89j1klm2nop3pqrs",
                          description="the file's uuid/address"),
    "device": fields.String(example="12abc34d5efg67hi89j1klm2nop3pqrs",
                            description="the device's uuid owning this device"),
    "filename": fields.String(example="foo.bar",
                              description="the file's name"),
    "content": fields.String(example="lorem ipsum dolor sit amet",
                             description="the files's content")
})

FileUpdateRequestSchema = api.model("File Update Request", {
    "filename": fields.String(required=True,
                              example="foo.bar",
                              description="the name of the file"),
    "content": fields.String(required=True,
                             example="lorem ipsum dolor sit amet",
                             description="the content of the file")
})

FileCreateRequestSchema = api.model("File Create Request Schema", {
    "filename": fields.String(required=True,
                              example="foo.bar",
                              description="the name of the file"),
    "content": fields.String(required=True,
                             example="lorem ipsum dolor sit amet",
                             description="the content of the file"),
    "device": fields.String(required=True,
                            example="12abc34d5efg67hi89j1klm2nop3pqrs",
                            description="uuid of device")
})

FileGetAllResponseSchema = api.model("File Get All Response", {
    "files": fields.List(fields.Nested(FileResponseSchema),
                         example="[{}, {}]",
                         description="a list of files")
})

file_api = Namespace('file')


@file_api.route('/<string:device>')
@file_api.doc("Private File Application Programming Interface")
class FileAPI(Resource):

    @file_api.doc("Get all files of a device")
    @file_api.marshal_with(FileGetAllResponseSchema)
    @file_api.response(400, "Invalid Input", ErrorSchema)
    @file_api.response(403, "No Access", ErrorSchema)
    @file_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def get(self, session, device):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=device).first()

        if device is None:
            abort(404, "unknown device")

        return {
            "files": FileModel.query.filter_by(device=device.uuid).all()
        }

    @file_api.doc("Change name of device")
    @file_api.marshal_with(FileResponseSchema)
    @file_api.expect(FileCreateRequestSchema, validate=True)
    @file_api.response(400, "Invalid Input", ErrorSchema)
    @file_api.response(403, "No Access", ErrorSchema)
    @file_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def put(self, session, device):
        filename: str = request.json["filename"]
        content: str = request.json["content"]

        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=device).first()

        if device is None:
            abort(404, "unknown device")

        file_count: int = (db.session.query(func.count(FileModel.uuid)).filter(FileModel.device == device.uuid)
                           .filter(FileModel.filename == filename)).first()[0]

        if file_count > 0:
            abort(400, "filename already taken")

        if len(content) > CONTENT_LENGTH:
            abort(400, "content is too big")

        file: Optional[FileModel] = FileModel.create(device.uuid, filename, content)

        db.session.add(file)
        db.session.commit()

        return file.serialize


@file_api.route('/<string:device>/<string:uuid>')
@file_api.doc("Public File Application Programming Interface")
class FileModificationAPI(Resource):

    @file_api.doc("Get information about a file")
    @file_api.marshal_with(FileResponseSchema)
    @file_api.response(400, "Invalid Input", ErrorSchema)
    @file_api.response(403, "No Access", ErrorSchema)
    @file_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def get(self, session, device, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=device).first()

        if device is None:
            abort(404, "unknown device")

        file: Optional[FileModel] = FileModel.query.filter_by(uuid=uuid).first()

        if file is None:
            abort(404, "invalid file uuid")

        return file.serialize

    @file_api.doc("Update a file")
    @file_api.marshal_with(FileResponseSchema)
    @file_api.expect(FileUpdateRequestSchema, validate=True)
    @file_api.response(400, "Invalid Input", ErrorSchema)
    @file_api.response(403, "No Access", ErrorSchema)
    @file_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def post(self, session, device, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=device).first()

        if device is None:
            abort(404, "unknown device")

        filename: str = request.json["filename"]
        content: str = request.json["content"]

        file: Optional[FileModel] = FileModel.query.filter_by(uuid=uuid).first()

        if file is None:
            abort(404, "invalid file uuid")

        file_count: int = (db.session.query(func.count(FileModel.uuid)).filter(FileModel.device == device.uuid)
                           .filter(FileModel.filename == filename)).first()[0]

        if file.filename != filename and file_count > 0:
            abort(400, "filename already taken")

        if len(content) > CONTENT_LENGTH:
            abort(400, "content is too big")

        file.filename = filename
        file.content = content

        db.session.commit()

        return file.serialize

    @file_api.doc("Delete a file")
    @file_api.marshal_with(SuccessSchema)
    @file_api.response(400, "Invalid Input", ErrorSchema)
    @file_api.response(403, "No Access", ErrorSchema)
    @file_api.response(404, "Not Found", ErrorSchema)
    @require_session
    def delete(self, session, device, uuid):
        device: Optional[DeviceModel] = DeviceModel.query.filter_by(uuid=device).first()

        if device is None:
            abort(404, "unknown device")

        file: Optional[FileModel] = FileModel.query.filter_by(uuid=uuid).first()

        if file is None:
            abort(404, "invalid file uuid")

        db.session.delete(file)
        db.session.commit()

        return {
            "ok": True
        }
