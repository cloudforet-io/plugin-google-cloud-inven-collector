import logging
import time

from spaceone.inventory.connector.pub_sub.subscription import SubscriptionConnector
from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.libs.schema.base import ReferenceModel
from spaceone.inventory.model.pub_sub.subscription.cloud_service import SubscriptionResource, SubscriptionResponse
from spaceone.inventory.model.pub_sub.subscription.cloud_service_type import CLOUD_SERVICE_TYPES
from spaceone.inventory.model.pub_sub.subscription.data import Subscription

_LOGGER = logging.getLogger(__name__)


class SubscriptionManager(GoogleCloudManager):
    connector_name = 'SubscriptionConnector'
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
        _LOGGER.debug(f'** Pub/Sub Subscription START **')

        start_time = time.time()
        collected_cloud_services = []
        error_responses = []
        subscription_id = ""

        secret_data = params['secret_data']
        project_id = secret_data['project_id']

        ##################################
        # 0. Gather All Related Resources
        # List all information through connector
        ##################################
        subscription_conn: SubscriptionConnector = self.locator.get_connector(self.connector_name, **params)
        subscriptions = subscription_conn.list_subscriptions()

        for subscription in subscriptions:
            try:
                ##################################
                # 1. Set Basic Information
                ##################################
                subscription_name = subscription.get('name')
                subscription_id = self._make_subscription_id(subscription_name, project_id)
                push_config = subscription.get('pushConfig')
                bigquery_config = subscription.get('bigqueryConfig')

                ##################################
                # 2. Make Base Data
                ##################################
                subscription_display = {
                    'delivery_type': self._make_delivery_type(push_config, bigquery_config),
                    'message_ordering': self._change_boolean_to_enabled_or_disabled(
                        subscription.get('enableMessageOrdering')),
                    'exactly_once_delivery': self._change_boolean_to_enabled_or_disabled(
                        subscription.get('enableExactlyOnceDelivery')),
                    'attachment': self._make_enable_attachment(subscription.get('topic')),
                    'retain_acked_messages': self._make_retain_yes_or_no(subscription.get('retainAckedMessages'))
                }

                if message_reduction_duration := subscription.get('messageRetentionDuration'):
                    subscription_display.update(
                        {'retention_duration': self._make_time_to_dhms_format(message_reduction_duration)}
                    )

                if expiration_policy := subscription.get('expirationPolicy'):
                    ttl = self._make_time_to_dhms_format(expiration_policy.get('ttl'))
                    subscription_display.update({'ttl': ttl,
                                                 'subscription_expiration': self._make_expiration_description(ttl)})

                if ack_deadline_seconds := subscription.get('ackDeadlineSeconds'):
                    subscription_display.update(
                        {'ack_deadline_seconds': self._make_time_to_dhms_format(ack_deadline_seconds)}
                    )

                if retry_policy := subscription.get('retryPolicy'):
                    subscription_display.update(
                        {'retry_policy': {'description': 'Retry after exponential backoff delay',
                                          'minimum_backoff': self._make_time_to_dhms_format(
                                              retry_policy.get('minimumBackoff')),
                                          'maximum_backoff': self._make_time_to_dhms_format(
                                              retry_policy.get('maximumBackoff'))}})
                else:
                    subscription_display.update(
                        {'retry_policy': {'description': 'Retry immediately'}})

                ##################################
                # 3. Make subscription data
                ##################################
                subscription.update({
                    'id': subscription_id,
                    'project': project_id,
                    'display': subscription_display
                })
                subscription_data = Subscription(subscription, strict=False)

                ##################################
                # 4. Make SubscriptionResource Code
                ##################################
                subscription_resource = SubscriptionResource({
                    'name': subscription_name,
                    'account': project_id,
                    'tags': subscription_data.labels,
                    'region_code': 'Global',
                    'instance_type': '',
                    'instance_size': 0,
                    'data': subscription_data,
                    'reference': ReferenceModel(subscription_data.reference())
                })

                ##################################
                # 5. Make Resource Response Object
                ##################################
                collected_cloud_services.append(SubscriptionResponse({'resource': subscription_resource}))

            except Exception as e:
                _LOGGER.error(f'[collect_cloud_service] => {e}', exc_info=True)
                error_response = self.generate_resource_error_response(e, 'Pub/Sub', 'Subscription', subscription_id)
                error_responses.append(error_response)

        _LOGGER.debug(f'** Pub/Sub Subscription Finished {time.time() - start_time} Seconds **')
        return collected_cloud_services, error_responses

    def _make_time_to_dhms_format(self, duration):
        if isinstance(duration, int):
            return self._display_time(duration)
        if isinstance(duration, str):
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

    @staticmethod
    def _make_delivery_type(push_config, bigquery_config):
        if push_config:
            delivery_type = 'Push'
        elif bigquery_config:
            delivery_type = 'BigQuery'
        else:
            delivery_type = 'Pull'
        return delivery_type

    @staticmethod
    def _make_subscription_id(subscription_name, project_id):
        path, topic_id = subscription_name.split(f'projects/{project_id}/subscriptions/')
        return topic_id

    @staticmethod
    def _change_boolean_to_enabled_or_disabled(boolean_field):
        if boolean_field:
            return 'Enabled'
        else:
            return 'Disabled'

    @staticmethod
    def _make_enable_attachment(topic):
        if topic == '_deleted-topic_':
            return 'Unattached'
        else:
            return 'Attached'

    @staticmethod
    def _make_retain_yes_or_no(retain_acked_messages):
        if retain_acked_messages:
            return 'Yes'
        else:
            return 'No'

    @staticmethod
    def _make_expiration_description(ttl):
        return f'Subscription expires in {ttl} if there is no activity'
