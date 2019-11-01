import app


# noinspection PyUnresolvedReferences
def load_endpoints():
    import resources.device
    import resources.file
    import resources.hardware


if __name__ == "__main__":
    load_endpoints()
    app.m.run()
