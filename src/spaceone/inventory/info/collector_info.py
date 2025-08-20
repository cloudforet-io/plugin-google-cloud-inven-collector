__all__ = ["PluginInfo", "ResourceInfo", "FirebaseProjectsInfo"]

from spaceone.api.inventory.plugin import collector_pb2
from spaceone.core.pygrpc.message_type import *


def PluginInfo(result):
    result["metadata"] = change_struct_type(result["metadata"])

    return collector_pb2.PluginInfo(**result)


def ResourceInfo(resource_dict):
    if "match_rules" in resource_dict:
        resource_dict.update(
            {"match_rules": change_struct_type(resource_dict["match_rules"])}
        )

    if "resource" in resource_dict:
        resource_dict.update(
            {"resource": change_struct_type(resource_dict["resource"])}
        )

    return collector_pb2.ResourceInfo(**resource_dict)


def FirebaseProjectsInfo(result):
    """
    Firebase 프로젝트 목록 정보를 반환합니다.
    """
    if "projects" in result:
        result["projects"] = change_struct_type(result["projects"])

    return collector_pb2.FirebaseProjectsInfo(**result)
