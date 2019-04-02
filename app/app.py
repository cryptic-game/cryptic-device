from cryptic import MicroService
from typing import Any, Dict, List
from objects import Base, engine

m: MicroService = MicroService('device')


if __name__ == '__main__':
    import resources.device
    import resources.file

    Base.metadata.create_all(bind=engine)
    m.run()
