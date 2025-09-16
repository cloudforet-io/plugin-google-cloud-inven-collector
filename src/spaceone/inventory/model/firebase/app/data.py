from schematics import Model
from schematics.types import IntType, ModelType, StringType, FloatType

from spaceone.inventory.libs.schema.cloud_service import CloudServiceMeta, BaseResource
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    BadgeDyField,
    TextDyField,
    EnumDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
)

"""
Firebase App Data Model
"""


class FirebaseAnalytics(Model):
    """Firebase Analytics 메트릭"""

    # 사용자 관련 메트릭
    active_users_1d = IntType(default=0)
    active_users_7d = IntType(default=0)
    active_users_30d = IntType(default=0)
    new_users = IntType(default=0)

    # 세션 관련 메트릭
    sessions = IntType(default=0)
    avg_session_duration = FloatType(default=0.0)
    bounce_rate = FloatType(default=0.0)

    # 이벤트 관련 메트릭
    events_count = IntType(default=0)
    screen_views = IntType(default=0)


class FirebasePerformance(Model):
    """Firebase Performance Monitoring 메트릭"""

    # 앱 시작 시간
    app_start_time_avg = FloatType(default=0.0)
    app_start_time_p90 = FloatType(default=0.0)
    app_start_time_p95 = FloatType(default=0.0)

    # 화면 렌더링 시간
    screen_rendering_avg = FloatType(default=0.0)
    screen_rendering_p90 = FloatType(default=0.0)

    # 네트워크 요청 메트릭
    network_requests_count = IntType(default=0)
    network_response_time_avg = FloatType(default=0.0)
    network_success_rate = FloatType(default=0.0)


class FirebaseCrashlytics(Model):
    """Firebase Crashlytics 메트릭"""

    # 크래시 관련 메트릭
    crash_count = IntType(default=0)
    crash_free_sessions = FloatType(default=0.0)
    crash_free_users = FloatType(default=0.0)

    # 안정성 메트릭
    stability_score = FloatType(default=0.0)
    affected_users = IntType(default=0)


class FirebaseCloudMessaging(Model):
    """Firebase Cloud Messaging (FCM) 메트릭"""

    # 메시지 전송 통계
    messages_sent = IntType(default=0)
    messages_delivered = IntType(default=0)
    messages_opened = IntType(default=0)

    # 전달률 및 오픈율
    delivery_rate = FloatType(default=0.0)
    open_rate = FloatType(default=0.0)

    # 토큰 관련
    active_tokens = IntType(default=0)


class FirebaseMonitoring(Model):
    """Firebase 통합 모니터링 메트릭"""

    analytics = ModelType(FirebaseAnalytics, serialize_when_none=False)
    performance = ModelType(FirebasePerformance, serialize_when_none=False)
    crashlytics = ModelType(FirebaseCrashlytics, serialize_when_none=False)
    cloud_messaging = ModelType(FirebaseCloudMessaging, serialize_when_none=False)


class App(BaseResource):
    """Firebase 앱 정보 모델 (App Engine과 동일하게 BaseResource 상속)"""

    # 핵심 식별 정보 (BaseResource의 name 필드 재사용)
    display_name = StringType(deserialize_from="displayName")
    platform = StringType()
    app_id = StringType(deserialize_from="appId")
    state = StringType()

    # API 메타데이터
    namespace = StringType()
    api_key_id = StringType(deserialize_from="apiKeyId")
    expire_time = StringType(deserialize_from="expireTime", serialize_when_none=False)

    # 프로젝트 정보 (BaseResource의 project 필드 재사용 가능하지만 호환성을 위해 유지)
    project_id = StringType(deserialize_from="projectId")

    # Firebase 특화 모니터링
    firebase_monitoring = ModelType(FirebaseMonitoring, serialize_when_none=False)

    def reference(self):
        project_id = self.project_id or ""
        app_id = self.app_id or ""
        return {
            "resource_id": self.app_id,
            "external_link": f"https://console.firebase.google.com/project/{project_id}/settings/general/{app_id}",
        }


# Firebase App 메타데이터 레이아웃
firebase_app_meta = CloudServiceMeta.set_layouts(
    layouts=[
        ItemDynamicLayout.set_fields(
            "App Information",
            fields=[
                TextDyField.data_source("Display Name", "data.display_name"),
                TextDyField.data_source("App ID", "data.app_id"),
                EnumDyField.data_source(
                    "Platform",
                    "data.platform",
                    default_badge={
                        "indigo.500": ["IOS"],
                        "green.500": ["ANDROID"],
                        "blue.500": ["WEB"],
                    },
                ),
                TextDyField.data_source("Namespace", "data.namespace"),
                BadgeDyField.data_source("State", "data.state"),
                TextDyField.data_source("API Key ID", "data.api_key_id"),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Google Cloud Monitoring",
            fields=[
                TextDyField.data_source(
                    "Monitoring Name",
                    "data.google_cloud_monitoring.name",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Resource ID",
                    "data.google_cloud_monitoring.resource_id",
                    options={"is_optional": True},
                ),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Google Cloud Logging",
            fields=[
                TextDyField.data_source(
                    "Logging Name",
                    "data.google_cloud_logging.name",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Resource ID",
                    "data.google_cloud_logging.resource_id",
                    options={"is_optional": True},
                ),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Firebase Analytics",
            fields=[
                TextDyField.data_source(
                    "Active Users (1D)",
                    "data.firebase_monitoring.analytics.active_users_1d",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Active Users (7D)",
                    "data.firebase_monitoring.analytics.active_users_7d",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Active Users (30D)",
                    "data.firebase_monitoring.analytics.active_users_30d",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "New Users",
                    "data.firebase_monitoring.analytics.new_users",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Sessions",
                    "data.firebase_monitoring.analytics.sessions",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Avg Session Duration (sec)",
                    "data.firebase_monitoring.analytics.avg_session_duration",
                    options={"is_optional": True},
                ),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Firebase Performance",
            fields=[
                TextDyField.data_source(
                    "App Start Time (Avg ms)",
                    "data.firebase_monitoring.performance.app_start_time_avg",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "App Start Time (P90 ms)",
                    "data.firebase_monitoring.performance.app_start_time_p90",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Network Requests",
                    "data.firebase_monitoring.performance.network_requests_count",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Network Response Time (Avg ms)",
                    "data.firebase_monitoring.performance.network_response_time_avg",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Network Success Rate (%)",
                    "data.firebase_monitoring.performance.network_success_rate",
                    options={"is_optional": True},
                ),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Firebase Crashlytics",
            fields=[
                TextDyField.data_source(
                    "Crash Count",
                    "data.firebase_monitoring.crashlytics.crash_count",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Crash-Free Sessions (%)",
                    "data.firebase_monitoring.crashlytics.crash_free_sessions",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Crash-Free Users (%)",
                    "data.firebase_monitoring.crashlytics.crash_free_users",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Stability Score",
                    "data.firebase_monitoring.crashlytics.stability_score",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Affected Users",
                    "data.firebase_monitoring.crashlytics.affected_users",
                    options={"is_optional": True},
                ),
            ],
        ),
        ItemDynamicLayout.set_fields(
            "Firebase Cloud Messaging",
            fields=[
                TextDyField.data_source(
                    "Messages Sent",
                    "data.firebase_monitoring.cloud_messaging.messages_sent",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Messages Delivered",
                    "data.firebase_monitoring.cloud_messaging.messages_delivered",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Messages Opened",
                    "data.firebase_monitoring.cloud_messaging.messages_opened",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Delivery Rate (%)",
                    "data.firebase_monitoring.cloud_messaging.delivery_rate",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Open Rate (%)",
                    "data.firebase_monitoring.cloud_messaging.open_rate",
                    options={"is_optional": True},
                ),
                TextDyField.data_source(
                    "Active Tokens",
                    "data.firebase_monitoring.cloud_messaging.active_tokens",
                    options={"is_optional": True},
                ),
            ],
        ),
    ]
)
