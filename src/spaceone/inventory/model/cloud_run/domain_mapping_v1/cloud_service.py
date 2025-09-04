from schematics.types import ModelType, PolyModelType, StringType

from spaceone.inventory.libs.schema.cloud_service import (
    CloudServiceMeta,
    CloudServiceResource,
    CloudServiceResponse,
)
from spaceone.inventory.libs.schema.metadata.dynamic_field import (
    DateTimeDyField,
    TextDyField,
)
from spaceone.inventory.libs.schema.metadata.dynamic_layout import (
    ItemDynamicLayout,
)
from spaceone.inventory.model.cloud_run.domain_mapping_v1.data import DomainMapping

"""
Cloud Run Domain Mapping
"""
# TAB - Domain Mapping Overview
domain_mapping_overview = ItemDynamicLayout.set_fields(
    "Domain Mapping Overview",
    fields=[
        TextDyField.data_source("API Version", "data.api_version"),
        TextDyField.data_source("Kind", "data.kind"),
        TextDyField.data_source("Name", "data.metadata.name"),
        TextDyField.data_source("Namespace", "data.metadata.namespace"),
        TextDyField.data_source("UID", "data.metadata.uid"),
        TextDyField.data_source("Cluster Name", "data.metadata.cluster_name"),
        DateTimeDyField.data_source(
            "Creation Timestamp", "data.metadata.creation_timestamp"
        ),
    ],
)

# TAB - Domain Mapping Spec
domain_mapping_spec = ItemDynamicLayout.set_fields(
    "Domain Mapping Spec",
    fields=[
        TextDyField.data_source("Route Name", "data.spec.route_name"),
        TextDyField.data_source("Certificate Mode", "data.spec.certificate_mode"),
    ],
)

# TAB - Domain Mapping Status
domain_mapping_status = ItemDynamicLayout.set_fields(
    "Domain Mapping Status",
    fields=[
        TextDyField.data_source(
            "Observed Generation", "data.status.observed_generation"
        ),
        TextDyField.data_source("URL", "data.status.url"),
        TextDyField.data_source("Condition Type", "data.status.conditions.type"),
        TextDyField.data_source("Condition Status", "data.status.conditions.status"),
        TextDyField.data_source("Condition Reason", "data.status.conditions.reason"),
        TextDyField.data_source("Condition Message", "data.status.conditions.message"),
        DateTimeDyField.data_source(
            "Condition Last Transition Time",
            "data.status.conditions.last_transition_time",
        ),
    ],
)

cloud_run_domain_mapping_meta = CloudServiceMeta.set_layouts(
    [
        domain_mapping_overview,
        domain_mapping_spec,
        domain_mapping_status,
    ]
)


class CloudRunResource(CloudServiceResource):
    cloud_service_group = StringType(default="CloudRun")


class DomainMappingResource(CloudRunResource):
    cloud_service_type = StringType(default="DomainMapping")
    data = ModelType(DomainMapping)
    _metadata = ModelType(
        CloudServiceMeta,
        default=cloud_run_domain_mapping_meta,
        serialized_name="metadata",
    )


class DomainMappingResponse(CloudServiceResponse):
    resource = PolyModelType(DomainMappingResource)
