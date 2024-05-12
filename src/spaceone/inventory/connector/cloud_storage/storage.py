import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["StorageConnector"]
_LOGGER = logging.getLogger(__name__)

MAX_OBJECTS = 100000


class StorageConnector(GoogleCloudConnector):
    google_client_service = "storage"
    version = "v1"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_buckets(self, **query):
        bucket_list = []
        query.update({"project": self.project_id, "projection": "full", "alt": "json"})
        request = self.client.buckets().list(**query)
        while request is not None:
            response = request.execute()
            for template in response.get("items", []):
                bucket_list.append(template)
            request = self.client.buckets().list_next(
                previous_request=request, previous_response=response
            )

        return bucket_list

    def list_iam_policy(self, bucket_name, **query):
        query.update({"bucket": bucket_name})
        result = self.client.buckets().getIamPolicy(**query).execute()

        return result

    def list_objects(self, bucket_name, **query):
        objects_list = []
        query.update({"bucket": bucket_name})
        count = 0
        request = self.client.objects().list(**query)
        while request is not None:
            response = request.execute()
            result = response.get("items", [])
            count = count + len(result)
            for template in result:
                objects_list.append({"size": template["size"]})
            # Max iteration
            if count > MAX_OBJECTS:
                # TOO MANY objects
                return False
            request = self.client.objects().list_next(
                previous_request=request, previous_response=response
            )
        return objects_list
