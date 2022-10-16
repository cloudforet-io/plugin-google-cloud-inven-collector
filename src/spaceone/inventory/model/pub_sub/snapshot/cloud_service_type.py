import os
from spaceone.inventory.libs.schema.cloud_service_type import *

current_dir = os.path.abspath(os.path.dirname(__file__))

cst_pub_sub_snapshot = CloudServiceTypeResource()
cst_pub_sub_snapshot.name = 'Instance'
cst_pub_sub_snapshot.provider = 'google_cloud'
cst_pub_sub_snapshot.group = 'ComputeEngine'
cst_pub_sub_snapshot.service_code = 'Compute Engine'
cst_pub_sub_snapshot.labels = ['Compute', 'Server']
cst_pub_sub_snapshot.is_primary = True
cst_pub_sub_snapshot.is_major = True
cst_pub_sub_snapshot.tags = {}

cst_pub_sub_snapshot._metadata = CloudServiceTypeMeta.set_meta(
    fields=[],
    search=[],
    widget=[]
)

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_pub_sub_snapshot}),
]
