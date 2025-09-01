from schematics import Model
from schematics.types import (
    BaseType,
    BooleanType,
    DictType,
    StringType,
)


class Connection(Model):
    name = StringType()
    create_time = StringType(deserialize_from="createTime")
    update_time = StringType(deserialize_from="updateTime")
    github_config = DictType(BaseType, deserialize_from="githubConfig", default={})
    github_enterprise_config = DictType(
        BaseType, deserialize_from="githubEnterpriseConfig", default={}
    )
    gitlab_config = DictType(BaseType, deserialize_from="gitlabConfig", default={})
    bitbucket_data_center_config = DictType(
        BaseType, deserialize_from="bitbucketDataCenterConfig", default={}
    )
    bitbucket_cloud_config = DictType(
        BaseType, deserialize_from="bitbucketCloudConfig", default={}
    )
    installation_state = DictType(
        BaseType, deserialize_from="installationState", default={}
    )
    disabled = BooleanType(default=False)
    reconciling = BooleanType(default=False)
    annotations = DictType(StringType, default={})
    etag = StringType()
    uid = StringType()
