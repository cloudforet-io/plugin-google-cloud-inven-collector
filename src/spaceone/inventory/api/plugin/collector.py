import logging

from spaceone.api.inventory.plugin import collector_pb2, collector_pb2_grpc
from spaceone.core.pygrpc import BaseAPI
from spaceone.inventory.service import CollectorService

_LOGGER = logging.getLogger(__name__)


class Collector(BaseAPI, collector_pb2_grpc.CollectorServicer):
    pb2 = collector_pb2
    pb2_grpc = collector_pb2_grpc

    def init(self, request, context):
        params, metadata = self.parse_request(request, context)

        with self.locator.get_service("CollectorService", metadata) as collector_svc:
            data = collector_svc.init(params)
            return self.locator.get_info("PluginInfo", data)

    def verify(self, request, context):
        params, metadata = self.parse_request(request, context)

        collector_svc: CollectorService = self.locator.get_service(
            "CollectorService", metadata
        )

        with collector_svc:
            collector_svc.verify(params)
            return self.locator.get_info("EmptyInfo")

    def collect(self, request, context):
        params, metadata = self.parse_request(request, context)

        collector_svc: CollectorService = self.locator.get_service(
            "CollectorService", metadata
        )

        # Collector main process
        with collector_svc:
            for resource in collector_svc.collect(params):
                yield self.locator.get_info("ResourceInfo", resource)

    def get_firebase_apps(self, request, context):
        """
        특정 프로젝트의 Firebase 앱들을 조회합니다.
        Firebase Management API의 searchApps 엔드포인트를 사용합니다.
        """
        params, metadata = self.parse_request(request, context)

        collector_svc: CollectorService = self.locator.get_service(
            "CollectorService", metadata
        )

        with collector_svc:
            apps = collector_svc.get_firebase_projects(params)
            return self.locator.get_info("FirebaseAppsInfo", apps)
