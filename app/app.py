from cryptic import MicroService
from objects import Base, engine

m: MicroService = MicroService('device')

if __name__ == '__main__':
    from resources.device import *
    from resources.file import *

    Base.metadata.create_all(bind=engine)
    m.run()
