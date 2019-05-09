from cryptic import MicroService, _config

import argparse

parser: argparse.ArgumentParser = argparse.ArgumentParser()

parser.add_argument('--debug', help='run this service with sqlite instead of mysql only for use in develop environment',
                    default=False, action='store_true')

args: argparse.Namespace = parser.parse_args()

if args.debug is True:

    mode: str = "debug"

else:

    mode: str = "prod"

_config.set_mode(mode)

m: MicroService = MicroService('device')

if __name__ == '__main__':
    from resources.device import *
    from resources.file import *

    m.Base.metadata.create_all(bind=m.engine)
    m.run()
