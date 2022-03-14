__all__ = ['PluginInfo', 'ResourceInfo']

from spaceone.api.inventory.plugin import collector_pb2
from spaceone.core.pygrpc.message_type import *


def PluginInfo(result):
    result['metadata'] = change_struct_type(result['metadata'])

    return collector_pb2.PluginInfo(**result)


def ResourceInfo(resource_dict):
    if 'match_rules' in resource_dict:
        resource_dict.update({
            'match_rules': change_struct_type(resource_dict['match_rules'])
        })

    if 'resource' in resource_dict:
        resource_dict.update({
            'resource': change_struct_type(resource_dict['resource'])
        })

    return collector_pb2.ResourceInfo(**resource_dict)
