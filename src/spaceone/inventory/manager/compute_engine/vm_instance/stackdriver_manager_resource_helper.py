from spaceone.inventory.libs.manager import GoogleCloudManager
from spaceone.inventory.model.compute_engine.instance.data import StackDriver, StackDriverFilters


class StackDriverManagerResourceHelper(GoogleCloudManager):

    connector_name = 'VMInstanceConnector'

    def get_stackdriver_info(self, instance_id):
        '''
        cloudwatch_data = {
                       'type': 'gce_instance',
                       'filters': [{
                           'key': 'resource.labels.instance_id',
                           'value': '1873022307818018997'
                       }]
                   }
        '''

        stackdriver_data = {
            'type': 'gce_instance',
            'filters': self.get_filters(instance_id)
        }

        return StackDriver(stackdriver_data, strict=False)

    @staticmethod
    def get_filters(instance_id):
        '''
        "filters": [
            {
                "key": "resource.labels.instance_id",
                "value": instacne_name
            }
        ]
        '''

        filter = {
            'key': 'resource.labels.instance_id',
            'value': instance_id
        }

        return [StackDriverFilters(filter, strict=False)]