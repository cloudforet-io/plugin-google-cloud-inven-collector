import logging

from spaceone.core import utils
from spaceone.inventory.libs.connector import GoogleCloudConnector
from datetime import datetime, timezone

__all__ = ['MonitoringConnector']
_LOGGER = logging.getLogger(__name__)

PERCENT_METRIC = ['10^2.%']


class MonitoringConnector(GoogleCloudConnector):
    google_client_service = 'monitoring'
    version = 'v3'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_metric_data(self, bucket_name, metric, start, end):

        start = self.date_time_to_iso(start)
        end = self.date_time_to_iso(end)
        metric_data = self.list_metrics_time_series(bucket_name, metric, start, end)

        return metric_data

    def get_metric_data_query(self, bucket_name, metric, start, end, **query):
        '''
            SAMPLE
            "name": 'projects/286919713412',
            "aggregation.alignmentPeriod": '362880s',
            "aggregation.crossSeriesReducer": 'REDUCE_NONE',
            "aggregation.perSeriesAligner": 'ALIGN_SUM',
            "filter": 'metric.type="compute.googleapis.com/instance/cpu/utilization" AND resource.type="gce_instance"',
            "interval.endTime" : 2020-08-09T04:48:00Z,
            "interval.startTime": 2020-08-06T00:00:00Z,
            "view": 'FULL'
        '''
        metric_filter = f'metric.type="{metric}" AND resource.labels.bucket_name="{bucket_name}"'

        query.update({
            'name': f'projects/{self.project_id}',
            'filter': metric_filter,
            'interval_endTime': end,
            'interval_startTime': start,
            'view': 'FULL'
        })
        return query

    def list_metrics_time_series(self, bucket_name, metric, start, end, **query):
        query = self.get_metric_data_query(bucket_name, metric, start, end, **query)

        response = self.client.projects().timeSeries().list(**query).execute()
        if 'timeSeries' in response:
            return response.get('timeSeries')[0]
        else:
            return {}

    @staticmethod
    def date_time_to_iso(date_time):
        date_format = date_time.isoformat()
        return date_format[0:date_format.find('+')] + 'Z' if '+' in date_format else date_format + 'Z'

