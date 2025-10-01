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
            # items가 존재하고 None이 아닌지 확인
            items = response.get("items", [])
            if items:
                for template in items:
                    # template이 딕셔너리인지 확인
                    if template is not None and isinstance(template, dict):
                        bucket_list.append(template)
                    else:
                        _LOGGER.warning(f"Skipping invalid bucket template: {type(template)}")
            request = self.client.buckets().list_next(
                previous_request=request, previous_response=response
            )

        return bucket_list

    def list_iam_policy(self, bucket_name, is_payer_bucket, **query):
        query.update({"bucket": bucket_name})
        if is_payer_bucket:
            query["userProject"] = self.project_id

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
            if result:
                count = count + len(result)
                for template in result:
                    if template and isinstance(template, dict):
                        # size 필드가 있는지 확인
                        size = template.get("size", "0")
                        objects_list.append({"size": size})
                    else:
                        _LOGGER.warning(f"Skipping invalid object template: {type(template)}")
            # Max iteration
            if count > MAX_OBJECTS:
                # TOO MANY objects
                return False
            request = self.client.objects().list_next(
                previous_request=request, previous_response=response
            )
        return objects_list
