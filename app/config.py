import os
from typing import Tuple, Union, List

to_load: List[Union[Tuple[str,str],Tuple[str,int]]] = [
    ("MYSQL_HOSTNAME", "localhost"),
    ("MYSQL_PORT", 3306),
    ("MYSQL_DATABASE", "crytpic"),
    ("MYSQL_USERNAME", "cryptic"),
    ("MYSQL_PASSWORD", "cryptic"),

    ("STORAGE_LOCATION", "data/")
]

config: dict = {}

for key in to_load:
    if isinstance(key, tuple):
        if key[0] in os.environ:
            config[key[0]] = os.environ.get(key[0])
        else:
            config[key[0]] = key[1]
    elif key in os.environ:
        config[key] = os.environ.get(key)

config["SQLALCHEMY_DATABASE_URI"]: str = \
    f"mysql+pymysql://{config['MYSQL_USERNAME']}:{config['MYSQL_PASSWORD']}@" \
        f"{config['MYSQL_HOSTNAME']}:{config['MYSQL_PORT']}/{config['MYSQL_DATABASE']}"