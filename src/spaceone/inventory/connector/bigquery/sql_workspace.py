import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ['SQLWorkspaceConnector']
_LOGGER = logging.getLogger(__name__)


class SQLWorkspaceConnector(GoogleCloudConnector):
    google_client_service = 'bigquery'
    version = 'v2'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_dataset(self, **query):
        dataset_list = []
        query.update({'projectId': self.project_id, 'all': True})
        request = self.client.datasets().list(**query)
        while request is not None:
            response = request.execute()
            for dataset in response.get('datasets', []):
                dataset_list.append(dataset)
            request = self.client.datasets().list_next(previous_request=request, previous_response=response)

        return dataset_list

    def get_dataset(self, dataset_id, **query):
        query.update({'projectId': self.project_id,
                      'datasetId': dataset_id})
        response = {}
        response = self.client.datasets().get(**query).execute()

        return response

    def list_job(self, **query):
        job_list = []
        query.update({'projectId': self.project_id,
                      'allUsers': True,
                      'projection': 'full'})
        request = self.client.jobs().list(**query)
        while request is not None:
            response = request.execute()
            for job in response.get('jobs', []):
                job_list.append(job)
            request = self.client.jobs().list_next(previous_request=request, previous_response=response)

        return job_list

    def list_projects(self, **query):
        project_list = []
        request = self.client.projects().list(**query)

        while request is not None:
            response = request.execute()
            for project in response.get('projects', []):
                project_list.append(project)
            request = self.client.projects().list_next(previous_request=request, previous_response=response)

        return project_list

    def list_tables(self, dataset_id, **query):
        table_list = []

        query.update({'projectId': self.project_id,
                      'datasetId': dataset_id})

        request = self.client.tables().list(**query)
        while request is not None:
            response = request.execute()
            for table in response.get('tables', []):
                table_list.append(table)
            request = self.client.tables().list_next(previous_request=request, previous_response=response)

        return table_list

    def get_tables(self, dataset_id, table_id, **query):
        query.update({'projectId': self.project_id,
                      'datasetId': dataset_id,
                      'tableId': table_id})
        response = {}
        response = self.client.tables().get(**query).execute()

        return response
