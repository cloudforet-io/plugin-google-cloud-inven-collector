<h1 align="center">Google Cloud Collector</h1>  

<br/>  
<div align="center" style="display:flex;">  
  <img width="245" src="https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud/Google_Cloud.svg">
  <p> 
    <br>
    <img alt="Version"  src="https://img.shields.io/badge/version-0.5.2-blue.svg?cacheSeconds=2592000"  />    
    <a href="https://www.apache.org/licenses/LICENSE-2.0"  target="_blank"><img alt="License: Apache 2.0"  src="https://img.shields.io/badge/License-Apache 2.0-yellow.svg" /></a> 
  </p> 
</div>    

**Plugin to collect Google Cloud**

> SpaceONE's [plugin-google-cloud-inven-collector](https://github.com/spaceone-dev/plugin-google-cloud-inven-collector) is a convenient tool to
get cloud service data from Google Cloud platform.


Find us also at [Dockerhub](https://hub.docker.com/repository/docker/spaceone/plugin-google-cloud-inven-collector)


Please contact us if you need any further information. (<support@spaceone.dev>)

---


<br>
<br>

### Google Service Endpoint (in use)
There is an endpoints used to collect resources information of GCP. Endpoint of served GCP is a URL consisting of a service code.
```text
https://[service-code].googleapis.com
```

We use dozens of endpoints because we collect information from many services.

<br>
<br>

### Service list

The following is a list of services being collected and service code information.

|No.|Service name|Service Code|
|---|------|---|
|1|Compute Engine|compute|
|2|Networking|compute|
|3|Cloud SQL|sqladmin|
|4|Storage|storage|
|5|BigQuery|bigquery|
|6|Cloud Pub/Sub|pubsub|
|7|Cloud Functions|cloudfunctions|
|8|Recommender|recommender|
|9|Firebase|firebase

If you want to know the detailed service endpoint, please check the [content details](###content-details) below.

<br>
<br>

### Content details

* Table of Contents
    * [Compute Engine](#compute-engine)
        * [VM Instance](#vm-instance)
        * [Instance Template](#instance-template)
        * [Instance Group](#instance-group)
        * [Machine Images](#machine-images)
        * [Disk](#disk)
        * [Snapshot](#snapshot)
    * [Networking](#networking)
        * [VPC Network](#vpc-network)
        * [Route](#route)
        * [External IP Address](#external-ip-address)
        * [Firewall](#firewall)
        * [LoadBalancing](#loadbalancing)
    * [Cloud SQL](#cloud-sql)
        * [Instance](#instance)
    * [Storage](#storage)
        * [Buckets](#Bucket)
    * [BigQuery](#bigquery)
        * [SQLWorkspace](#SQLWorkspace)
    * [Cloud Pub/Sub](#cloud-pub/sub)
        * [Topic](#topic)
        * [Subscription](#subscription)
        * [Snapshot](#snapshot)
        * [Schema](#schema)
    * [Cloud Fuctions](#cloud-functions)
        * [Function](#function)
    * [Recommender](#recommender)
        * [Recommendation](#recommendation)
        * [Insight](#insight)
    * [Firebase](#firebase)
        * [Project](#project)
    * [Options](#options)
      * [CloudServiceType](#cloud-service-type--specify-what-to-collect)
      * [ServiceCodeMapper](#service-code-mapper--update-service-code-in-cloud-service-type)

<br>
<br>

## Authentication Overview
Registered service account on SpaceONE must have certain permissions to collect cloud service data
Please, set authentication privilege for followings:

#### [Compute Engine](https://cloud.google.com/compute/docs/apis)

- ##### VM Instance
    - Scopes
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/cloud-platform

    - IAM
        - compute.zones.list
        - compute.regions.list
        - compute.instances.list
        - compute.machineTypes.list
        - compute.urlMaps.list
        - compute.backendServices.list
        - compute.disks.list
        - compute.diskTypes.list
        - compute.autoscalers.list
        - compute.images.list
        - compute.subnetworks.list
        - compute.regionUrlMaps.list
        - compute.backendServices.list
        - compute.targetPools.list
        - compute.forwardingRules.list

    - Service Endpoint
        - https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/global/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/zone/{zone}/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/{resource_name}

- ##### Instance Template
    - Scopes
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/cloud-platform

    - IAM
        - compute.instanceGroupManagers.list
        - compute.machineTypes.list
        - compute.disks.list
        - compute.instanceTemplates.list

    - Service Endpoint
        - https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/global/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/zone/{zone}/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/{resource_name}

- ##### Instance Group
    - Scopes
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/cloud-platform

    - IAM
        - compute.instanceGroups.list
        - compute.instanceGroupManagers.list
        - compute.instances.list
        - compute.autoscalers.list
        - compute.instanceTemplates.list

    - Service Endpoint
        - https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/global/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/zone/{zone}/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/{resource_name}

- #### Machine Images
    - Scopes
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/cloud-platform

    - IAM
        - compute.machineImages.list
        - compute.machineTypes.list
        - compute.disks.list
        - compute.images.list

    - Service Endpoint
        - https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/global/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/zone/{zone}/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/{resource_name}

- #### Disk
    - Scopes
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/cloud-platform

    - IAM
        - compute.disks.list
        - compute.resourcePolicies.list

    - Service Endpoint
        - https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/global/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/zone/{zone}/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/{resource_name}

- #### Snapshot
    - Scopes
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/cloud-platform

    - IAM
        - compute.snapshots.list
        - compute.resourcePolicies.list
        - compute.disks.list

    - Service Endpoint
        - https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/global/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/zone/{zone}/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/{resource_name}


#### [Networking](https://cloud.google.com/compute/docs/apis)

- #### VPC Network
    - Scopes
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/cloud-platform

    - IAM
        - compute.instances.list
        - compute.forwardingRules.list
        - compute.networks.list
        - compute.addresses.list
        - compute.globalAddresses.list
        - compute.subnetworks.list
        - compute.firewalls.list
        - compute.routes.list

    - Service Endpoint
        - https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/global/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/zone/{zone}/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/{resource_name}

- #### Route
    - Scopes
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/cloud-platform

    - IAM
        - compute.routes.list
        - compute.instances.list

    - Service Endpoint
        - https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/global/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/zone/{zone}/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/{resource_name}

- #### External IP Address
    - Scopes
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/cloud-platform

    - IAM
        - compute.instances.list
        - compute.forwardingRules.list
        - compute.addresses.list

    - Service Endpoint
        - https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/global/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/zone/{zone}/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/{resource_name}

- #### Firewall
    - Scopes
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/cloud-platform

    - IAM
        - compute.instances.list
        - compute.firewalls.list

    - Service Endpoint
        - https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/global/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/zone/{zone}/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/{resource_name}

- #### LoadBalancing
    - Scopes
        - https://www.googleapis.com/auth/compute
        - https://www.googleapis.com/auth/cloud-platform

    - IAM
        - compute.urlMaps.list
        - compute.backendBuckets.list
        - compute.backendServices.list
        - compute.targetPools.list
        - compute.forwardingRules.list
        - compute.targetGrpcProxies.list
        - compute.targetHttpProxies.list
        - compute.targetHttpsProxies.list
        - compute.targetGrpcProxies.list
        - compute.healthChecks.list
        - compute.httpHealthChecks.list
        - compute.httpsHealthChecks.list
        - compute.autoscalers.list

    - Service Endpoint
        - https://compute.googleapis.com/compute/v1/projects/{project}/aggregated/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/global/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/zone/{zone}/{resource_name}
        - https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/{resource_name}


#### [Cloud SQL](https://cloud.google.com/sql/docs/mysql/apis)
- #### Instance
    - Scopes
        - https://www.googleapis.com/auth/cloud-platform
        - https://www.googleapis.com/auth/sqlservice.admin

    - IAM
        - sqladmin.instances.list
        - sqladmin.databases.list
        - sqladmin.users.list
        - sqladmin.backup_runs.list

    - Service Endpoint
        - https://sqladmin.googleapis.com/v1/projects/{project}/{resources}
        - https://sqladmin.googleapis.com/v1/projects/{project}/instances/{instance}/{resources}



#### [Storage](https://cloud.google.com/storage/docs/apis)
- #### Bucket
    - IAM
        - storage.buckets.get
        - storage.objects.list
        - storage.objects.getIamPolicy

    - Service Endpoint
        - https://storage.googleapis.com/storage/v1/b/{resource}


#### [BigQuery](https://cloud.google.com/bigquery/docs/reference)
- #### SQLWorkspace
    - IAM
        - bigquery.datasets.get
        - bigquery.tables.get
        - bigquery.tables.list
        - bigquery.jobs.list
        - resourcemanager.projects.get

    - Service Endpoint
        - https://bigquery.googleapis.com/bigquery/v2/projects/{projectId}/{resource}


#### [Pub/Sub](https://cloud.google.com/pubsub/docs/reference)
- #### Topic
    - IAM
        - pubsub.topics.list
        - pubsub.subscriptions.get
        - pubsub.snapshots.get

    - Service Endpoint
        - https://pubsub.googleapis.com/v1/{project}/topics
        - https://pubsub.googleapis.com/v1/{subscription}
        - https://pubsub.googleapis.com/v1/{snapshot}
- #### Subscription
    - IAM
        - pubsub.subscriptions.list

    - Service Endpoint
        - https://pubsub.googleapis.com/v1/{project}/subscriptions
- #### Snapshot
    - IAM
        - pubsub.snapshots.list

    - Service Endpoint
        - https://pubsub.googleapis.com/v1/{project}/snapshots
- #### Schema
    - IAM
        - pubsub.schemas.list

    - Service Endpoint
        - https://pubsub.googleapis.com/v1/{parent}/schemas

#### [Functions](https://cloud.google.com/functions/docs/reference)
- #### Function
    - IAM
        - 1st Generation
          - cloudfunctions.functions.list
          - storage.bucket.get
        - 2nd Generation
          - cloudfunctions.functions.list
          - storage.bucket.get
          - eventarc.providers.list

    - Service Endpoint
        - 1st Generation
          - https://cloudfunctions.googleapis.com/v1/{parent=projects/*/locations/*}/functions
          - https://storage.googleapis.com/storage/v1/b/{bucket}
        - 2nd Generation
          - https://cloudfunctions.googleapis.com/v2/{parent=projects/*/locations/*}/functions
          - https://storage.googleapis.com/storage/v1/b/{bucket}
          - https://eventarc.googleapis.com/v1/{parent=projects/*/locations/*}/providers

#### [Recommender](https://cloud.google.com/recommender/docs/overview)
- #### Recommendation & Insight
    - IAM
        - cloudasset.assets.listResource
        - cloudasset.assets.listIamPolicy
        - cloudasset.assets.listOrgPolicy
        - cloudasset.assets.listAccessPolicy
        - cloudasset.assets.listOSInventories
        - recommender.*.get
        - recommender.*.list

    - Recommendation Service Endpoint
        - https://recommender.googleapis.com/v1/{name=projects/*/locations/*/recommenders/*/recommendations/*}

    - Insight Service Endpoint
        - https://cloudasset.googleapis.com/v1/{parent=*/*}/assets
        - https://recommender.googleapis.com/v1/{parent=projects/*/locations/*/insightTypes/*}/insights

#### [Firebase](https://firebase.google.com/docs/reference/firebase-management/rest)
- #### Project
    - IAM
        - firebase.projects.searchApps
        - firebase.projects.get

    - Service Endpoint
        - https://firebase.googleapis.com/v1beta1/projects/{parent}/searchApps

---

## Firebase

### Project

Firebase 프로젝트 정보를 수집합니다. Firebase Management API의 `searchApps` 엔드포인트를 사용하여 특정 프로젝트의 Firebase 앱들을 가져옵니다.

#### 수집되는 정보:
- Project ID
- Display Name
- Project Number
- State (ACTIVE, DELETED 등)
- Firebase Apps (iOS, Android, Web 앱들)
- Platform Statistics (플랫폼별 앱 개수)
- App Count (총 앱 개수)

#### 사용 예시:
```bash
# Firebase 프로젝트만 수집
{
    "cloud_service_types": ["Firebase"]
}
```

---

## Options

### Cloud Service Type : Specify what to collect

If `cloud_service_types` is added to the list elements in options, only the specified cloud service type is collected.
By default, if cloud_service_types is not specified in options, all services are collected.

The cloud_service_types items that can be specified are as follows.

<pre>
<code>
{
    "cloud_service_types": [
    'ComputeEngine'
    'CloudSQL',
    'BigQuery',
    'CloudStorage',
    'Networking'
    ]
}
</code>
</pre>

How to update plugin information using spacectl is as follows.
First, create a yaml file to set options.

<pre>
<code>
> cat update_collector.yaml
---
collector_id: collector-xxxxxxx
options:
  cloud_service_types:
    - CloudSQL
    - VPCNetwork
</code>
</pre>

Update plugin through spacectl command with the created yaml file.

<pre><code>
> spacectl exec update_plugin inventory.Collector -f update_collector.yaml
</code></pre>


### Service Code Mapper : Update service code in Cloud Service Type.

If `service_code_mapper` is in options, You can replace the existed service code into new value one. 
The default service code is listed below [service code list](#service-list) 
<pre>
<code>
{
    "service_code_mappers": {
        "Compute Engine": "Your new service code",
        "Cloud SQL": "Your new service code",
    }
}
</code>
</pre>

### Custom Asset URL : Update ASSET_URL  in Cloud Service Type.

If `custom_asset_url` is in options, You can change it to an asset_url that users will use instead of the default asset_url.  
The default ASSET_URL in cloud_service_conf is 
`https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/google_cloud`.

<pre>
<code>
{
    "custom_asset_url": "https://xxxxx.spaceone.dev/icon/google"
}
</code>
</pre>

---