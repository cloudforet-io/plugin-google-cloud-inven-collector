import time
import logging

from spaceone.inventory.connector.pub_sub.topic import TopicConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.model.pub_sub.topic.cloud_service_type import CLOUD_SERVICE_TYPES

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
        topic_names = topic_conn.list_project_topic_names()

        for topic_name in topic_names:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                topic_id = self._make_topic_id(topic_name, project_id)

                ##################################
                # 2. Make Base Data
                ##################################

                subscription_names = topic_conn.list_subscription_names(topic_name)
                for subscription_name in subscription_names:
                    subscription = topic_conn.get_subscription(subscription_name)
                    print(subscription)
                # TODO : create Subscription model

                snapshot_names = topic_conn.list_snapshot_names(topic_name)
                for snapshot_name in snapshot_names:
                    snapshot = topic_conn.get_snapshot(snapshot_name)
                    # print(snapshot)

                ##################################
                # 3. Make Return Resource
                ##################################

                ##################################
                # 4. Make Collected Region Code
                ##################################

                ##################################
                # 5. Make Resource Response Object
                # List of LoadBalancingResponse Object
                ##################################

            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'Pub/Sub', 'Topic', topic_name)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Firewall Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    @staticmethod
    def _make_topic_id(topic_name, project_id):
        path, topic_id = topic_name.split(f'projects/{project_id}/topics/')
        return topic_id
