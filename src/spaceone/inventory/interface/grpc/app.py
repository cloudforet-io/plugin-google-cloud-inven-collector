from spaceone.inventory.api.plugin.collector import Collector


class GrpcApp:
    def __init__(self):
        self.services = []

    def add_service(self, service_cls):
        self.services.append(service_cls)

    def get_services(self):
        return self.services


def create_app():
    app = GrpcApp()
    app.add_service(Collector)
    return app


app = create_app()
