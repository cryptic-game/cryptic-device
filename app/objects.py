from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from config import config

directory = config["STORAGE_LOCATION"]

if not os.path.exists(directory):
    os.makedirs(directory)

engine = create_engine('sqlite:///' + directory + 'device.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()
session: Session = Session()
