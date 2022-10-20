import time
import logging
from datetime import datetime, timedelta

from spaceone.inventory.connector.pub_sub.topic import TopicConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.pub_sub.topic.cloud_service import TopicResource, TopicResponse
from spaceone.inventory.model.pub_sub.topic.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.pub_sub.topic.data import Topic, Subscription, Snapshot

_LOGGER = logging.getLogger(__name__)


class TopicManager(GoogleCloudManager):
    connector_name = 'TopicConnector'
    cloud_service_types = CLOUD_SERVICE_TYPES

    def collect_cloud_service(self, params):
        """
        Args:
            params:
                - options
                - schema
                - secret_data
                - filter
                - zones
        Response:
            CloudServiceResponse/ErrorResourceResponse
        """
        _LOGGER.debug(f'[Pub/Sub] Topic START')

        start_time = time.time()
        collected_cloud_services = []
        error_responses = []
        topic_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        topic_conn: TopicConnector = self.locator.get_connector(self.connector_name, **params)
        topics = topic_conn.list_topics()

        for topic in topics:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                topic_name = topic.get('name')
                topic_id = self._make_topic_id(topic_name, project_id)
                labels = topic.get('label')
                message_storage_policy = topic.get('messageStoragePolicy')
                kms_key_name = topic.get('kmsKeyName')
                schema_settings = topic.get('schemaSettings')
                satisfies_pzs = topic.get('stisfiesPzs')
                message_retention_duration = topic.get('messageRetentionDuration')

                ##################################
                # 2. Make Base Data
                ##################################
                subscriptions = []
                subscription_names = topic_conn.list_subscription_names(topic_name)
                for subscription_name in subscription_names:
                    subscription = topic_conn.get_subscription(subscription_name)
                    subscriptions.append(Subscription(subscription, strict=False))

                snapshots = []
                snapshot_names = topic_conn.list_snapshot_names(topic_name)
                for snapshot_name in snapshot_names:
                    snapshot = topic_conn.get_snapshot(snapshot_name)
                    snapshots.append(Snapshot(snapshot, strict=False))

                display = {
                    'subscription_count': len(subscription_names),
                    'encryption_key': self._get_encryption_key(kms_key_name),
                }
                if message_retention_duration:
                    display.update({'retention': self._change_duration_to_dhm(message_retention_duration)})

                ##################################
                # 3. Make topic data
                ##################################
                topic.update({
                    'project': project_id,
                    'labels': labels,
                    'message_storage_policy': message_storage_policy,
                    'kms_key_name': kms_key_name,
                    'schema_settings': schema_settings,
                    'satisfies_pzs': satisfies_pzs,
                    'message_retention_duration': message_retention_duration,
                    'subscriptions': subscriptions,
                    'snapshots': snapshots,
                    'display': display
                })
                topic_data = Topic(topic, strict=False)
                ##################################
                # 4. Make TopicResource Code
                ##################################
                topic_resource = TopicResource({
                    'name': topic_id,
                    'account': project_id,
                    'tags': labels,
                    'region_code': 'Global',
                    'instance_type': '',
                    'instance_size': 0,
                    'data': topic_data,
                    'reference': ReferenceModel(topic_data.reference())
                })
                ##################################
                # 5. Make Resource Response Object
                ##################################
                collected_cloud_services.append(TopicResponse({'resource': topic_resource}))
            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'Pub/Sub', 'Topic', topic_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Pub/Sub Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    @staticmethod
    def _make_topic_id(topic_name, project_id):
        path, topic_id = topic_name.split(f'projects/{project_id}/topics/')
        return topic_id

    @staticmethod
    def _get_encryption_key(kms_key_name):
        if kms_key_name:
            encryption_key = 'Customer managed'
        else:
            encryption_key = 'Google managed'
        return encryption_key

    def _change_duration_to_dhm(self, duration):
        seconds, _ = duration.split('s')
        return self._display_time(int(seconds))

    @staticmethod
    def _display_time(seconds, granularity=2):
        result = []
        intervals = (
            ('days', 86400),
            ('hr', 3600),
            ('min', 60),
            ('seconds', 1),
        )
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append(f"{value} {name}")
        return ' '.join(result[:granularity])
