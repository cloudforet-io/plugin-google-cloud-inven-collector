import os
from spaceone.inventory.libs.schema.cloud_service_type import *

current_dir = os.path.abspath(os.path.dirname(__file__))

cst_pub_sub_schema = CloudServiceTypeResource()
cst_pub_sub_schema.name = 'Instance'
cst_pub_sub_schema.provider = 'google_cloud'
cst_pub_sub_schema.group = 'ComputeEngine'
cst_pub_sub_schema.service_code = 'Compute Engine'
cst_pub_sub_schema.labels = ['Compute', 'Server']
cst_pub_sub_schema.is_primary = True
cst_pub_sub_schema.is_major = True
cst_pub_sub_schema.tags = {}

cst_pub_sub_schema._metadata = CloudServiceTypeMeta.set_meta(
    fields=[],
    search=[],
    widget=[]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_pub_sub_schema}),
]
