from cryptic import MicroService, Config, DatabaseWrapper

m: MicroService = MicroService("device")

wrapper: DatabaseWrapper = m.get_wrapper()
