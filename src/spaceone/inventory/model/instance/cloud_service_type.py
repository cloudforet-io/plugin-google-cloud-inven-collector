from spaceone.inventory.libs.schema.cloud_service_type import CloudServiceTypeResource, CloudServiceTypeResponse

cst_vm_instance = CloudServiceTypeResource()
cst_vm_instance.resource_type = 'inventory.Server'
cst_vm_instance.name = 'Instance'
cst_vm_instance.provider = 'google_cloud'
cst_vm_instance.group = 'ComputeEngine'
cst_vm_instance.service_code = 'Compute Engine'
cst_vm_instance.labels = ['Compute']
cst_vm_instance.is_primary = True
cst_vm_instance.is_major = True
cst_vm_instance.tags = {
    'spaceone:icon': 'https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Compute_Engine.svg',
}

CLOUD_SERVICE_TYPES = [
    CloudServiceTypeResponse({'resource': cst_vm_instance}),
]

