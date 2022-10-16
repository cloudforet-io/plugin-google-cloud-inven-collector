import os
from spaceone.inventory.libs.schema.cloud_service_type import *

current_dir = os.path.abspath(os.path.dirname(__file__))

cst_subscription = CloudServiceTypeResource()
cst_subscription.name = 'Instance'
cst_subscription.provider = 'google_cloud'
cst_subscription.group = 'ComputeEngine'
cst_subscription.service_code = 'Compute Engine'
cst_subscription.labels = ['Compute', 'Server']
cst_subscription.is_primary = True
cst_subscription.is_major = True
cst_subscription.tags = {}

cst_subscription._metadata = CloudServiceTypeMeta.set_meta(
    fields=[],
    search=[],
    widget=[]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_subscription}),
]
