import app

if __name__ == "__main__":
    from resources.device import *
    from resources.file import *
    from resources.hardware import *

    app.wrapper.Base.metadata.create_all(bind=wrapper.engine)
    app.m.run()
