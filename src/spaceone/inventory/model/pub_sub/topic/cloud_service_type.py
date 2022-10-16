import os
from spaceone.inventory.libs.schema.cloud_service_type import *

current_dir = os.path.abspath(os.path.dirname(__file__))

cst_topic = CloudServiceTypeResource()
cst_topic.name = 'Instance'
cst_topic.provider = 'google_cloud'
cst_topic.group = 'ComputeEngine'
cst_topic.service_code = 'Compute Engine'
cst_topic.labels = ['Compute', 'Server']
cst_topic.is_primary = True
cst_topic.is_major = True
cst_topic.tags = {}

cst_topic._metadata = CloudServiceTypeMeta.set_meta(
    fields=[],
    search=[],
    widget=[]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_topic}),
]
