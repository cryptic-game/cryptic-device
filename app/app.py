from cryptic import MicroService

from objects import Base, engine

m: MicroService = MicroService('device')

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)

    from resources.device import *
    from resources.file import *

    m.run()
