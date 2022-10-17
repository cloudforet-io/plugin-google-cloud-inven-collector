import os
from spaceone.inventory.libs.schema.cloud_service_type import *

current_dir = os.path.abspath(os.path.dirname(__file__))

cst_topic = CloudServiceTypeResource()
cst_topic.name = 'Topic'
cst_topic.provider = 'google_cloud'
cst_topic.group = 'Pub/Sub'
cst_topic.service_code = 'Cloud Pub/Sub'
cst_topic.labels = ['Application Integration']
cst_topic.is_primary = True
cst_topic.is_major = True
cst_topic.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/cloud_pubsub.svg'
}

cst_topic._metadata = CloudServiceTypeMeta.set_meta(
    fields=[],
    search=[],
    widget=[]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_topic}),
]
