from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from config import config
import argparse

parser: argparse.ArgumentParser = argparse.ArgumentParser()

parser.add_argument('--debug', help='run this service with sqlite instead of mysql only for use in develop environment',
                    default=False, action='store_true')

args: argparse.Namespace = parser.parse_args()

if args.debug is True:

    directory = config["STORAGE_LOCATION"]

    if not os.path.exists(directory):
        os.makedirs(directory)

    uri: str = 'sqlite:///' + directory + "service.db"

    engine: Engine = create_engine(uri)

else:

    engine: Engine = create_engine(config["SQLALCHEMY_DATABASE_URI"])

Session = sessionmaker(bind=engine)

session: Session = Session()

Base = declarative_base()