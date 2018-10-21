import os

to_load = [
    "MYSQL_HOSTNAME",
    "MYSQL_PORT",
    "MYSQL_DATABASE",
    "MYSQL_USERNAME",
    "MYSQL_PASSWORD",
    "CROSS_ORIGIN",
    "DEBUG"
]

# the final configuration dict
config = {}

# load all configuration values from the env
for key in to_load:
    config[key] = os.environ[key]


def get_database_uri() -> str:
    return "mysql+pymysql://" + str(config["MYSQL_USERNAME"]) + ":" + str(config["MYSQL_PASSWORD"] \
                            + "@" + str(config["MYSQL_HOSTNAME"]) + ":" + str(config["MYSQL_PORT"]) \
                                    + "/" + str(config["MYSQL_DATABASE"]))
