from schematics import Model
from schematics.types import ModelType, ListType, StringType, IntType, DateTimeType, BooleanType, FloatType, DictType, UnionType, MultiType


class Labels(Model):
    key = StringType()
    value = StringType()


class PeeringDisplay(Model):
    your_network = StringType(default='')
    peered_network = StringType(default='')
    project_id = StringType(default='')
    state_display = StringType(choices=('Inactive', 'Active'))
    ex_custom_route = StringType(default='None')
    ex_route_public_ip_display = StringType(default='')


class Peering(Model):
    name = StringType()
    network = StringType()
    state = StringType()
    state_details = StringType(deserialize_from='stateDetails', serialize_when_none=False)
    auto_create_routes = BooleanType(deserialize_from='autoCreateRoutes', serialize_when_none=False)
    export_custom_routes = BooleanType(deserialize_from='exportCustomRoutes', serialize_when_none=False)
    import_custom_routes = BooleanType(deserialize_from='importCustomRoutes', serialize_when_none=False)
    exchange_subnet_routes = BooleanType(deserialize_from='exchangeSubnetRoutes', serialize_when_none=False)
    export_subnet_routes_with_public_ip = BooleanType(deserialize_from='exportSubnetRoutesWithPublicIp', serialize_when_none=False)
    import_subnet_routes_with_public_ip = BooleanType(deserialize_from='importSubnetRoutesWithPublicIp', serialize_when_none=False)
    peer_Mtu = IntType(deserialize_from='peerMtu', serialize_when_none=False)
    display = ModelType(PeeringDisplay, serialize_when_none=False)


class SecondaryIpRanges(Model):
    range_name = StringType()
    ip_cidr_range = StringType()


class LogConfigSubnet(Model):
    enable = BooleanType(serialize_when_none=False)
    aggregation_interval = StringType(deserialize_from='aggregationInterval', serialize_when_none=False)
    flow_sampling = IntType(deserialize_from='flowSampling', serialize_when_none=False)
    metadata = StringType(deserialize_from='metadata', serialize_when_none=False)
    metadata_fields = ListType(StringType(), default=[], deserialize_from='metadataFields', serialize_when_none=False)
    filter_expr = StringType(deserialize_from='filterExpr', serialize_when_none=False)


class Subnetwork(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    network = StringType()
    region = StringType()
    google_access = StringType(choices=('On', 'Off'))
    flow_log = StringType(choices=('On', 'Off'))
    ip_cidr_range = StringType(deserialize_from='ipCidrRange')
    gateway_address = StringType(deserialize_from='gatewayAddress')
    secondary_ip_ranges = ListType(ModelType(SecondaryIpRanges), default=[], serialize_when_none=False)
    self_link = StringType(deserialize_from='selfLink')
    fingerprint = StringType()
    enable_flow_logs = BooleanType(deserialize_from='enableFlowLogs', serialize_when_none=False)
    private_ipv6_google_access = StringType(deserialize_from='privateIpv6GoogleAccess', serialize_when_none=False)
    ipv6_cidr_range = StringType(deserialize_from='ipv6CidrRange', serialize_when_none=False)
    purpose = StringType(choices=('PRIVATE_RFC_1918', 'INTERNAL_HTTPS_LOAD_BALANCER'), serialize_when_none=False)
    role = StringType(choices=('ACTIVE', 'BACKUP'), serialize_when_none=False)
    state = StringType(choices=('READY', 'DRAINING'), serialize_when_none=False)
    log_config = ModelType(LogConfigSubnet, serialize_when_none=False)
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')


class SubnetworkConfig(Model):
    total_number = IntType(default=0)
    subnets = ListType(ModelType(Subnetwork), default=[])


class Route(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    network = StringType()
    dest_range = StringType(deserialize_from='destRange')
    priority = IntType()
    tags = ListType(StringType(), default=[])
    nextHopInstance = StringType(deserialize_from='nextHopInstance', serialize_when_none=False)
    nextHopIp = StringType(deserialize_from='nextHopIp', serialize_when_none=False)
    nextHopNetwork = StringType(deserialize_from='nextHopNetwork', serialize_when_none=False)
    nextHopGateway = StringType(deserialize_from='nextHopGateway', serialize_when_none=False)
    nextHopPeering = StringType(deserialize_from='nextHopPeering', serialize_when_none=False)
    nextHopIlb = StringType(deserialize_from='nextHopIlb', serialize_when_none=False)
    next_hop = StringType()
    self_link = StringType(deserialize_from='selfLink')
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')


class RouteConfig(Model):
    total_number = IntType(default=0)
    route = ListType(ModelType(Route), default=[])


class VPNRoutingConfig(Model):
    routing_mode = StringType(choices=('REGIONAL', 'GLOBAL'), deserialize_from='routingMode')


class Allowed(Model):
    ip_protocol = StringType(deserialize_from='IPProtocol')
    ports = ListType(StringType())


class LogConfig(Model):
    enable = BooleanType(serialize_when_none=False)
    metadata = StringType(serialize_when_none=False)


class FirewallDisplay(Model):
    type_display = StringType()
    target_display = ListType(StringType(default=[]))
    filter = StringType(default='')
    protocols_port = ListType(StringType(), default=[])
    action = StringType(choices=('Allow', 'Deny'))
    logs = StringType(choices=('On', 'Off'))


class Firewall(Model):
    id = StringType()
    name = StringType()
    description = StringType()
    network = StringType()
    priority = IntType()
    direction = StringType()
    source_ranges = ListType(StringType(), deserialize_from='sourceRanges', serialize_when_none=False)
    destination_ranges = ListType(StringType(), deserialize_from='destinationRanges', serialize_when_none=False)
    source_tags = ListType(StringType(), deserialize_from='sourceTags', serialize_when_none=False)
    target_tags = ListType(StringType(), deserialize_from='targetTags', serialize_when_none=False)
    source_service_accounts = ListType(StringType(), deserialize_from='sourceServiceAccounts', serialize_when_none=False)
    target_service_accounts = ListType(StringType(), deserialize_from='targetServiceAccounts', serialize_when_none=False)
    allowed = ListType(ModelType(Allowed), serialize_when_none=False)
    denied = ListType(ModelType(Allowed), serialize_when_none=False)
    disabled = BooleanType(serialize_when_none=False)
    log_config = ModelType(LogConfig, deserialize_from='logConfig', serialize_when_none=False)
    self_link = StringType(deserialize_from='selfLink')
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')
    display = ModelType(FirewallDisplay, serialize_when_none=False)


class FirewallConfig(Model):
    total_number = IntType(default=0)
    firewall = ListType(ModelType(Firewall), default=[])


class IPAddress(Model):
    id = StringType(default='')
    name = StringType(default='')
    address = StringType()
    region = StringType()
    subnet_name = StringType()
    address_type = StringType(choices=('INTERNAL', 'EXTERNAL'), deserialize_from='addressType')
    is_ephemeral = StringType(choices=('Static', 'Ephemeral'))
    purpose = StringType(choices=('GCE_ENDPOINT', 'DNS_RESOLVER', 'VPC_PEERING', 'IPSEC_INTERCONNECT'), serialize_when_none=False)
    description = StringType()
    network_tier = StringType(deserialize_from='networkTier')
    used_by = ListType(StringType(), default=[])
    self_link = StringType(deserialize_from='selfLink')
    ip_version = StringType(choices=('IPV4', 'IPV6'), deserialize_from='ipVersion', serialize_when_none=False)
    ip_version_display = StringType()
    status = StringType(choices=('RESERVED', 'RESERVING', 'IN_USE'))
    users = ListType(StringType(), default=[])
    labels = ListType(ModelType(Labels), default=[])
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')


class VPCNetwork(Model):
    id = StringType()
    name = StringType()
    project = StringType()
    description = StringType()
    ipv4_range = StringType(deserialize_from='IPv4Range', serialize_when_none=False)
    gateway_ipv4 = StringType(deserialize_from='gatewayIPv4', serialize_when_none=False)
    self_link = StringType(deserialize_from='selfLink')
    subnet_creation_mode = StringType(choices=('Auto', 'Custom'))
    auto_create_subnetworks = BooleanType(deserialize_from='autoCreateSubnetworks')
    peerings = ListType(ModelType(Peering), default=[])
    mtu = IntType(default=1460)
    routing_config = ModelType(VPNRoutingConfig, deserialize_from='routingConfig')
    global_dynamic_route = StringType(choices=('On', 'Off'))
    dynamic_routing_mode = StringType(choices=('Regional', 'Global'))
    subnetwork_data = ModelType(SubnetworkConfig, default=[])
    ip_address_data = ListType(ModelType(IPAddress), default=[])
    firewall_data = ModelType(FirewallConfig, default=[])
    route_data = ModelType(RouteConfig, default=[])
    creation_timestamp = DateTimeType(deserialize_from='creationTimestamp')

    def reference(self):
        return {
            "resource_id": self.self_link,
            "external_link": f"https://console.cloud.google.com/networking/networks/details/{self.name}?project={self.project}"
        }