from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import config
from cryptic import MicroService

engine = create_engine('sqlite:///'+ config["STORAGE_LOCATION"])
Session = sessionmaker(bind=engine)
Base = declarative_base()
session: Session = Session()
