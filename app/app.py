from cryptic import MicroService, _config, DatabaseWrapper

import argparse

parser: argparse.ArgumentParser = argparse.ArgumentParser()

parser.add_argument('--debug', help='run this service with sqlite instead of mysql only for use in develop environment',
                    default=False, action='store_true')

args: argparse.Namespace = parser.parse_args()

if args.debug is True:

    mode: str = "debug"

else:

    mode: str = "production"

_config.set_mode(mode)

m: MicroService = MicroService('device')

wrapper : DatabaseWrapper = m.get_wrapper()

if __name__ == '__main__':
    from resources.device import *
    from resources.file import *

    wrapper.Base.metadata.create_all(bind=wrapper.engine)
    m.run()
