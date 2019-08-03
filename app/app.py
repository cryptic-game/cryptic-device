from cryptic import MicroService, Config, DatabaseWrapper, get_config

config: Config = get_config()  # / production

m: MicroService = MicroService("device")

wrapper: DatabaseWrapper = m.get_wrapper()

if __name__ == "__main__":
    import resources.device
    import resources.file
    import resources.hardware

    wrapper.Base.metadata.create_all(bind=wrapper.engine)
    m.run()
