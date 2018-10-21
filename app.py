"""The app module, containing the app factory function."""
from flask import Flask
from flask_cors import CORS
from time import sleep
from database import db
import config

from models.network import Network
from models.device import Device

from models.auth import User
from models.auth import Session

from blueprints.info import info


def create_app() -> Flask:
    """
    An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :return: The initialized flask app
    """

    app = Flask("cryptic")

    app.config["SQLALCHEMY_DATABASE_URI"] = config.get_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config.config["CROSS_ORIGIN"]:
        CORS(app)

    with app.app_context():
        db.init_app(app=app)
        while True:
            try:
                register_models()
                break
            except Exception as e:
                print(e)
                sleep(2)

    register_blueprints(app)

    return app


def register_models() -> None:
    """
    This function registers all database models.

    :return: None
    """
    db.create_all()
    db.session.commit()


def register_blueprints(app: Flask) -> None:
    """
    This function registers all flask blueprints.

    :param app: The "raw" flask app
    :return: None
    """
    app.register_blueprint(info, url_prefix="/info")
