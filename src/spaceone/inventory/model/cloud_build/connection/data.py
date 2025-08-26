from schematics import Model
from schematics.types import (
    BooleanType,
    DateTimeType,
    DictType,
    StringType,
)


class Connection(Model):
    name = StringType()
    create_time = DateTimeType(deserialize_from="createTime")
    update_time = DateTimeType(deserialize_from="updateTime")
    github_config = DictType(StringType, deserialize_from="githubConfig", default={})
    github_enterprise_config = DictType(StringType, deserialize_from="githubEnterpriseConfig", default={})
    gitlab_config = DictType(StringType, deserialize_from="gitlabConfig", default={})
    bitbucket_data_center_config = DictType(StringType, deserialize_from="bitbucketDataCenterConfig", default={})
    bitbucket_cloud_config = DictType(StringType, deserialize_from="bitbucketCloudConfig", default={})
    installation_state = DictType(StringType, deserialize_from="installationState", default={})
    disabled = BooleanType(default=False)
    reconciling = BooleanType(default=False)
    annotations = DictType(StringType, default={})
    etag = StringType()
    uid = StringType()
