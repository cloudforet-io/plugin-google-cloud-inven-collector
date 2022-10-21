import os

from spaceone.inventory.libs.schema.cloud_service_type import *

current_dir = os.path.abspath(os.path.dirname(__file__))

cst_subscription = CloudServiceTypeResource()
cst_subscription.name = 'Subscription'
cst_subscription.provider = 'google_cloud'
cst_subscription.group = 'Pub/Sub'
cst_subscription.service_code = 'Cloud Pub/Sub'
cst_subscription.labels = ['Application Integration']
cst_subscription.is_primary = True
cst_subscription.is_major = True
cst_subscription.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/cloud_pubsub.svg'
}

cst_subscription._metadata = CloudServiceTypeMeta.set_meta(
    fields=[],
    search=[],
    widget=[]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_subscription}),
]
