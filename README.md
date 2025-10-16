# Google Cloud Inventory Collector Plugin

Language: [English](README.md) | [한국어](README_KR.md)

SpaceONE's GCP (Google Cloud Platform) Inventory Collector plugin. The Inventory plugin automatically collects Google Cloud resource information.

## Table of Contents

1. [Overview](#overview)
2. [Plugin Setup and Deployment Guide](#plugin-setup-and-deployment-guide)
3. [Target Services for Collection](#target-services-for-collection)
4. [GCP Service Endpoints](#gcp-service-endpoints)
5. [Supported Regions List](#supported-regions-list)
6. [Service List](#service-list)
7. [Authentication Overview](#authentication-overview)
8. [IAM Permission Setup](#iam-permission-setup)
9. [Automated Permission Setup Scripts](#automated-permission-setup-scripts)
10. [Secret Data Configuration](#secret-data-configuration)
11. [Product Requirements Document (PRD)](#product-requirements-document-prd)
12. [Input Parameters](#input-parameters)

## Overview

This document provides resource collection methods and implementation guides for Google Cloud services supported by the SpaceONE Google Cloud Inventory Collector plugin.

## Plugin Setup and Deployment Guide

### Step 1: Register Plugin to Repository

Register the plugin to the Repository service so that SpaceONE can recognize the container image as a plugin.

#### 1.1 Create Plugin Registration YAML File

You need to modify the registry_type and image path appropriately according to your deployment environment.

```yaml
# register_plugin.yaml
capability: {}
image: plugin-google-cloud-inven-collector
labels:
- Compute Engine
- Networking
- Cloud SQL
name: plugin-google-cloud-inven-collector
plugin_id: plugin-google-cloud-inven-collector
provider: google_cloud
registry_config:
  image_pull_secret: aramco-gcr-json-key
  url: asia-northeast3-docker.pkg.dev/mkkang-project/mkkang-repository
registry_type: GCP_PRIVATE_GCR
resource_type: inventory.Collector
tags: {}
```

#### 1.2 Register Plugin

```bash
spacectl exec create repository.Plugin -f register_plugin.yaml
```

## Target Services for Collection

This plugin collects resources from the following Google Cloud services:

### Computing Services
- **Compute Engine**: Virtual machine instances and related resources (VM Instance, Disk, Snapshot, Machine Image, Instance Template, Instance Group)
- **App Engine**: Fully managed serverless platform (Application, Service, Version, Instance)
- **Kubernetes Engine (GKE)**: Managed Kubernetes cluster service (Cluster, Node Pool, Node, Node Group)
- **Cloud Run**: Container-based serverless platform (Service, Job, Execution, Task, Revision)
- **Cloud Functions**: Event-driven serverless functions (Gen1, Gen2)

### Data and Storage Services
- **Cloud Storage**: Object storage service
- **Cloud SQL**: Managed relational database
- **BigQuery**: Data warehouse and analytics service
- **Filestore**: Managed NFS file system
- **Firestore**: NoSQL document database
- **Datastore**: NoSQL document database (Datastore mode)

### Data Processing and Analytics
- **Dataproc**: Managed Apache Spark and Hadoop service
- **Batch**: Batch job processing service
- **Storage Transfer**: Data transfer service

### Development Tools and CI/CD
- **Cloud Build**: Continuous integration/deployment service
- **Firebase**: Mobile and web application development platform

### Security and Management
- **KMS (Key Management Service)**: Encryption key management service
- **Pub/Sub**: Messaging service
- **Networking**: Network resources
- **Recommender**: Resource optimization recommendations

## GCP Service Endpoints

Each Google Cloud service uses the following API endpoints:

| Service | API Endpoint | API Version |
|---------|-------------|-------------|
| App Engine | `https://appengine.googleapis.com` | v1, v1beta |
| Kubernetes Engine | `https://container.googleapis.com` | v1, v1beta1 |
| Compute Engine | `https://compute.googleapis.com` | v1 |
| Cloud Run | `https://run.googleapis.com` | v1, v2 |
| Cloud Storage | `https://storage.googleapis.com` | v1 |
| Cloud SQL | `https://sqladmin.googleapis.com` | v1 |
| BigQuery | `https://bigquery.googleapis.com` | v2 |
| Dataproc | `https://dataproc.googleapis.com` | v1 |
| Cloud Build | `https://cloudbuild.googleapis.com` | v1, v2 |
| Filestore | `https://file.googleapis.com` | v1, v1beta1 |
| Firestore | `https://firestore.googleapis.com` | v1 |
| Datastore | `https://datastore.googleapis.com` | v1 |
| Firebase | `https://firebase.googleapis.com` | v1beta1 |
| KMS | `https://cloudkms.googleapis.com` | v1 |
| Batch | `https://batch.googleapis.com` | v1 |
| Storage Transfer | `https://storagetransfer.googleapis.com` | v1 |

## Supported Regions List

This plugin can collect resources from the following Google Cloud regions:

### Asia Pacific Region
- `asia-east1` (Taiwan)
- `asia-east2` (Hong Kong)
- `asia-northeast1` (Tokyo)
- `asia-northeast2` (Osaka)
- `asia-northeast3` (Seoul)
- `asia-south1` (Mumbai)
- `asia-south2` (Delhi)
- `asia-southeast1` (Singapore)
- `asia-southeast2` (Jakarta)

### Europe Region
- `europe-central2` (Warsaw)
- `europe-north1` (Finland)
- `europe-southwest1` (Madrid)
- `europe-west1` (Belgium)
- `europe-west2` (London)
- `europe-west3` (Frankfurt)
- `europe-west4` (Netherlands)
- `europe-west6` (Zurich)
- `europe-west8` (Milan)
- `europe-west9` (Paris)

### North America Region
- `northamerica-northeast1` (Montreal)
- `northamerica-northeast2` (Toronto)
- `us-central1` (Iowa)
- `us-east1` (South Carolina)
- `us-east4` (Northern Virginia)
- `us-east5` (Columbus)
- `us-south1` (Dallas)
- `us-west1` (Oregon)
- `us-west2` (Los Angeles)
- `us-west3` (Salt Lake City)
- `us-west4` (Las Vegas)

### South America Region
- `southamerica-east1` (São Paulo)
- `southamerica-west1` (Santiago)

### Other Regions
- `australia-southeast1` (Sydney)
- `australia-southeast2` (Melbourne)
- `me-central1` (Doha)
- `me-west1` (Tel Aviv)

### Global Resources
- `global` (For global resources)

## Service List

Detailed information for currently implemented services:

### 1. Compute Engine
- **Description**: Google Cloud's virtual machine computing service
- **Collected Resources**: VM Instance, Disk, Snapshot, Machine Image, Instance Template, Instance Group
- **API Version**: v1
- **Documentation**: [Compute Engine Guide](./docs/ko/prd/compute_engine/README.md)

### 2. App Engine
- **Description**: Google Cloud's fully managed serverless platform
- **Collected Resources**: Application, Service, Version, Instance
- **API Version**: v1, v1beta (backward compatibility)
- **Documentation**: [App Engine Guide](./docs/ko/prd/app_engine/README.md)

### 3. Kubernetes Engine (GKE)
- **Description**: Google Cloud's managed Kubernetes cluster service
- **Collected Resources**: Cluster, Node Pool, Node, Node Group
- **API Version**: v1, v1beta (backward compatibility)
- **Documentation**: [Kubernetes Engine Guide](./docs/ko/prd/kubernetes_engine/README.md)

### 4. Cloud Run
- **Description**: Container-based serverless platform
- **Collected Resources**: Service, Job, Execution, Task, Revision, Worker Pool, Domain Mapping
- **API Version**: v1, v2 (complete version separation)
- **Documentation**: [Cloud Run Guide](./docs/ko/prd/cloud_run/README.md)

### 5. Cloud Functions
- **Description**: Event-driven serverless functions service
- **Collected Resources**: Function (Gen1, Gen2), Trigger, Environment Variables
- **API Version**: v1, v2 (complete generation separation)
- **Documentation**: [Cloud Functions Guide](./docs/ko/prd/cloud_functions/README.md)

### 6. Cloud Storage
- **Description**: Object storage service
- **Collected Resources**: Bucket, Lifecycle Policy, IAM Policy, Encryption Settings
- **API Version**: v1
- **Documentation**: [Cloud Storage Guide](./docs/ko/prd/cloud_storage/README.md)

### 7. Cloud SQL
- **Description**: Managed relational database service
- **Collected Resources**: Instance, Database, User, Backup Configuration
- **API Version**: v1
- **Documentation**: [Cloud SQL Guide](./docs/ko/prd/cloud_sql/README.md)

### 8. BigQuery
- **Description**: Data warehouse and analytics service
- **Collected Resources**: Dataset, Table, View, Job, Schema
- **API Version**: v2
- **Documentation**: [BigQuery Guide](./docs/ko/prd/bigquery/README.md)

### 9. Cloud Build
- **Description**: Continuous integration/deployment service
- **Collected Resources**: Build, Trigger, Worker Pool, Connection, Repository
- **API Version**: v1, v2 (complete version separation)
- **Documentation**: [Cloud Build Guide](./docs/ko/prd/cloud_build/README.md)

### 10. Dataproc
- **Description**: Managed Apache Spark and Hadoop service
- **Collected Resources**: Cluster, Job, Workflow Template, Autoscaling Policy
- **API Version**: v1
- **Documentation**: [Dataproc Guide](./docs/ko/prd/dataproc/README.md)

### 11. Filestore
- **Description**: Managed NFS file system
- **Collected Resources**: Instance, Backup, Snapshot
- **API Version**: v1, v1beta1
- **Documentation**: [Filestore Guide](./docs/ko/prd/filestore/README.md)

### 12. Firestore
- **Description**: NoSQL document database
- **Collected Resources**: Database, Collection, Index, Backup
- **API Version**: v1
- **Documentation**: [Firestore Guide](./docs/ko/prd/firestore/README.md)

### 13. Datastore
- **Description**: NoSQL document database (Datastore mode)
- **Collected Resources**: Database, Index, Namespace
- **API Version**: v1
- **Documentation**: [Datastore Guide](./docs/ko/prd/datastore/README.md)

### 14. Networking
- **Description**: Network infrastructure service
- **Collected Resources**: VPC Network, Subnet, Firewall, External IP, Load Balancer, Route, VPN Gateway
- **API Version**: v1
- **Documentation**: [Networking Guide](./docs/ko/prd/networking/README.md)

### 15. KMS (Key Management Service)
- **Description**: Encryption key management service
- **Collected Resources**: KeyRing, CryptoKey, CryptoKeyVersion
- **API Version**: v1
- **Documentation**: [KMS Guide](./docs/ko/prd/kms/README.md)

### 16. Pub/Sub
- **Description**: Messaging and event streaming service
- **Collected Resources**: Topic, Subscription, Schema, Snapshot
- **API Version**: v1
- **Documentation**: [Pub/Sub Guide](./docs/ko/prd/pubsub/README.md)

### 17. Firebase
- **Description**: Mobile and web application development platform
- **Collected Resources**: Project
- **API Version**: v1beta1
- **Documentation**: [Firebase Guide](./docs/ko/prd/firebase/Google Firebase 제품 요구사항 정의서.md)

### 18. Batch
- **Description**: Batch job processing service
- **Collected Resources**: Job, Task
- **API Version**: v1
- **Documentation**: [Batch Guide](./docs/ko/prd/batch/Google Cloud Batch 제품 요구사항 정의서.md)

### 19. Storage Transfer
- **Description**: Data transfer service
- **Collected Resources**: Transfer Job, Transfer Operation, Agent Pool, Service Account
- **API Version**: v1
- **Documentation**: [Storage Transfer Guide](./docs/ko/prd/storage_transfer/README.md)

## Authentication Overview

Google Cloud Inventory Collector uses Service Account-based authentication to access Google Cloud APIs.

### Authentication Method
- **Service Account Key File**: Uses JSON format Service Account key file
- **OAuth 2.0**: Google Cloud API standard authentication method
- **Scope**: `https://www.googleapis.com/auth/cloud-platform` (Full Google Cloud platform access)

### Authentication Flow
1. Register Service Account key file to SpaceONE Secret
2. Plugin authenticates to Google Cloud API using the key file
3. Verify required IAM permissions for each service
4. Collect resources through API calls

## IAM Permission Setup

Minimum IAM permissions required for each Google Cloud service:

### Basic Permissions (Common to all services)
```json
{
  "roles": [
    "roles/viewer",
    "roles/browser"
  ]
}
```

### Service-specific Detailed Permissions

#### App Engine
```json
{
  "permissions": [
    "appengine.applications.get",
    "appengine.services.list",
    "appengine.versions.list",
    "appengine.instances.list"
  ]
}
```

#### Kubernetes Engine (GKE)
```json
{
  "permissions": [
    "container.clusters.list",
    "container.clusters.get",
    "container.nodePools.list",
    "container.nodePools.get",
    "container.nodes.list"
  ]
}
```

#### Cloud Run
```json
{
  "permissions": [
    "run.services.list",
    "run.services.get",
    "run.jobs.list",
    "run.executions.list",
    "run.tasks.list",
    "run.revisions.list"
  ]
}
```

#### Cloud Build
```json
{
  "permissions": [
    "cloudbuild.builds.list",
    "cloudbuild.triggers.list",
    "cloudbuild.workerpools.list",
    "source.repos.list"
  ]
}
```

#### Dataproc
```json
{
  "permissions": [
    "dataproc.clusters.list",
    "dataproc.clusters.get",
    "dataproc.jobs.list",
    "dataproc.workflowTemplates.list",
    "dataproc.autoscalingPolicies.list"
  ]
}
```

#### Storage & Database Services
```json
{
  "permissions": [
    "storage.buckets.list",
    "storage.objects.list",
    "file.instances.list",
    "datastore.databases.list",
    "datastore.indexes.list",
    "datastore.entities.list"
  ]
}
```

#### KMS
```json
{
  "permissions": [
    "cloudkms.keyRings.list",
    "cloudkms.cryptoKeys.list",
    "cloudkms.cryptoKeyVersions.list"
  ]
}
```

## Automated Permission Setup Scripts

Use the following scripts to automatically set up required IAM permissions:

### 1. Service Account Creation and Permission Grant
```bash
#!/bin/bash

# Variable settings
PROJECT_ID="your-project-id"
SERVICE_ACCOUNT_NAME="spaceone-collector"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="spaceone-collector-key.json"

# Create Service Account
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
    --display-name="SpaceONE Inventory Collector" \
    --description="Service account for SpaceONE Google Cloud inventory collection" \
    --project=${PROJECT_ID}

# Grant basic permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/viewer"

# Grant service-specific permissions
ROLES=(
    "roles/appengine.appViewer"
    "roles/container.viewer"
    "roles/run.viewer"
    "roles/cloudbuild.builds.viewer"
    "roles/dataproc.viewer"
    "roles/storage.objectViewer"
    "roles/file.viewer"
    "roles/datastore.viewer"
    "roles/cloudkms.viewer"
    "roles/firebase.viewer"
)

for role in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="${role}"
done

# Create Service Account key file
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SERVICE_ACCOUNT_EMAIL} \
    --project=${PROJECT_ID}

echo "Service Account setup completed."
echo "Key file: ${KEY_FILE}"
echo "Service Account Email: ${SERVICE_ACCOUNT_EMAIL}"
```

### 2. API Activation Script
```bash
#!/bin/bash

PROJECT_ID="your-project-id"

# Required API list
APIS=(
    "appengine.googleapis.com"
    "container.googleapis.com"
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "dataproc.googleapis.com"
    "storage.googleapis.com"
    "file.googleapis.com"
    "datastore.googleapis.com"
    "cloudkms.googleapis.com"
    "firebase.googleapis.com"
    "batch.googleapis.com"
    "storagetransfer.googleapis.com"
    "compute.googleapis.com"
)

# Enable APIs
for api in "${APIS[@]}"; do
    echo "Enabling ${api}..."
    gcloud services enable ${api} --project=${PROJECT_ID}
done

echo "All APIs have been enabled."
```

## Secret Data Configuration

How to configure Secret Data for using Google Cloud Inventory Collector in SpaceONE.

### Secret Data Format
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "spaceone-collector@your-project-id.iam.gserviceaccount.com",
  "client_id": "client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/spaceone-collector%40your-project-id.iam.gserviceaccount.com"
}
```

### Register Secret in SpaceONE Console
1. Navigate to **Asset > Service Account** menu
2. Click **+ Create** button
3. **Provider**: Select `Google Cloud`
4. **Secret Data**: Enter Service Account key file content in the above JSON format
5. Save with **Save** button

### Register Secret via CLI
```bash
# Register Secret using spacectl
spacectl exec register secret.secret \
    -p name="google-cloud-sa" \
    -p provider="google_cloud" \
    -p secret_type="CREDENTIALS" \
    -p data=@service-account-key.json
```

## Product Requirements Document (PRD)

Detailed Product Requirements Documents for each Google Cloud service can be found at the following links:

### Computing Services
- [App Engine PRD](./docs/ko/prd/app_engine/README.md) - Serverless application platform
- [Kubernetes Engine PRD](./docs/ko/prd/kubernetes_engine/README.md) - Managed Kubernetes service
- [Cloud Run PRD](./docs/ko/prd/cloud_run/README.md) - Container-based serverless platform

### Data and Storage
- [Filestore PRD](./docs/ko/prd/filestore/README.md) - Managed NFS file system
- [Firestore PRD](./docs/ko/prd/firestore/README.md) - NoSQL document database
- [Datastore PRD](./docs/ko/prd/datastore/README.md) - NoSQL database (Datastore mode)

### Data Processing and Analytics
- [Dataproc PRD](./docs/ko/prd/dataproc/README.md) - Managed Spark/Hadoop service
- [Batch PRD](./docs/ko/prd/batch/Google Cloud Batch 제품 요구사항 정의서.md) - Batch job processing
- [Storage Transfer PRD](./docs/ko/prd/storage_transfer/README.md) - Data transfer service

### Development Tools and CI/CD
- [Cloud Build PRD](./docs/ko/prd/cloud_build/README.md) - Continuous integration/deployment service
- [Firebase PRD](./docs/ko/prd/firebase/Google Firebase 제품 요구사항 정의서.md) - Mobile/web development platform

### Security and Management
- [KMS PRD](./docs/ko/prd/kms/README.md) - Encryption key management service

## Input Parameters

Google Cloud Inventory Collector supports the following input parameters:

### Required Parameters
```json
{
  "secret_data": {
    "type": "service_account",
    "project_id": "string",
    "private_key": "string",
    "client_email": "string"
  }
}
```

### Optional Parameters
```json
{
  "options": {
    "cloud_service_types": ["AppEngine", "KubernetesEngine", "CloudRun"],
    "region_filter": ["asia-northeast3", "us-central1"],
    "exclude_regions": ["europe-west1", "us-west1"],
    "kms_locations": ["global", "asia-northeast3"],
    "include_jobs": true,
    "database_filter": ["(default)", "custom-db"],
    "job_filter": ["active-jobs-only"]
  }
}
```

### Parameter Detailed Description

#### cloud_service_types
- **Type**: Array of String
- **Description**: Specify Google Cloud service types to collect
- **Default**: All services
- **Example**: `["AppEngine", "KubernetesEngine", "CloudRun", "CloudBuild"]`

#### region_filter
- **Type**: Array of String
- **Description**: Specify list of regions to collect
- **Default**: All regions
- **Example**: `["asia-northeast3", "us-central1", "global"]`

#### exclude_regions
- **Type**: Array of String
- **Description**: List of regions to exclude from collection
- **Default**: None
- **Example**: `["europe-west1", "us-west1"]`

#### kms_locations (KMS only)
- **Type**: Array of String
- **Description**: Specific location list to search for KMS KeyRings
- **Default**: Search all locations
- **Recommended**: `["global", "asia-northeast3"]`

#### include_jobs (Dataproc only)
- **Type**: Boolean
- **Description**: Whether to include Dataproc cluster job information
- **Default**: `false`

#### database_filter (Datastore/Firestore only)
- **Type**: Array of String
- **Description**: Specify list of databases to collect
- **Default**: All databases
- **Example**: `["(default)", "custom-database"]`

## Document Structure

```
docs/ko/
├── README.md                           # This file
├── guide/                             # General guides
├── development/                       # Development guides
└── prd/                              # Product Requirements Documents
    ├── app_engine/                    # App Engine domain
    │   ├── README.md                  # Comprehensive guide
    │   ├── API_Reference.md           # API reference
    │   └── Implementation_Guide.md    # Implementation guide
    ├── kubernetes_engine/             # Kubernetes Engine domain
    │   ├── README.md                  # Comprehensive guide
    │   ├── API_Reference.md           # API reference
    │   └── Implementation_Guide.md    # Implementation guide
    ├── storage_transfer/              # Storage Transfer domain
    ├── firestore/                     # Firestore domain
    ├── kms/                           # KMS domain
    ├── datastore/                     # Datastore domain
    ├── filestore/                     # Filestore domain
    ├── dataproc/                      # Dataproc domain
    ├── cloud_run/                     # Cloud Run domain
    └── cloud_build/                   # Cloud Build domain
```

## Key Features

### 1. Resource Collection
- **Hierarchical Collection**: Application → Service → Version → Instance structure
- **Batch Processing**: Efficient processing of large data
- **Parallel Processing**: Concurrent collection of multiple resources
- **Caching**: Minimize repetitive API calls

### 2. Error Handling
- **Retry Logic**: Automatic retry for transient errors
- **Detailed Error Messages**: Clear information for troubleshooting
- **Logging**: Detailed log recording for all operations

### 3. Performance Optimization
- **Timeout Management**: Appropriate timeout settings for each API call
- **Memory Efficiency**: Minimize memory usage through sequential processing
- **API Quota Management**: Prevent quota exceeded and optimization

### 4. Monitoring
- **Performance Metrics**: Performance indicators such as collection time and error rate
- **Status Tracking**: Monitor resource status and health
- **Health Check**: Real-time service status verification

## Architecture

### Service-Manager-Connector Structure
```
Service Layer (API endpoints)
    ↓
Manager Layer (Business logic)
    ↓
Connector Layer (Google Cloud API integration)
```

### Resource Collection Flow
1. **Initialization**: Load authentication information and settings
2. **Collection**: Query resource information through API
3. **Processing**: Add metadata and data cleansing
4. **Validation**: Data integrity and relationship verification
5. **Storage**: Store resources in SpaceONE inventory


### 3. Execution
```bash
# Basic collection execution
python -m spaceone.inventory.service.collector_service

# Collect specific service only
python -m spaceone.inventory.service.collector_service --service app_engine
```

## Development Guide

### 1. Adding New Service
1. **Implement Connector**: Google Cloud API integration
2. **Implement Manager**: Business logic and data processing
3. **Define Model**: Data structure and validation
4. **Write Tests**: Unit and integration tests
5. **Documentation**: API reference and implementation guide

### 2. Coding Rules
- **Naming Convention**: snake_case (variables, functions), PascalCase (classes)
- **Documentation**: Google style Docstring (in English)
- **Error Handling**: Specific exception handling and logging
- **Testing**: Write test code for all features

### 3. Quality Assurance
- **Linting**: Code style checking through Ruff
- **Formatting**: Apply automatic code formatting
- **Testing**: Test execution through pytest
- **Coverage**: Maintain code coverage above 80%

## Troubleshooting

### 1. Common Issues
- **Permission Error**: Check IAM roles and API activation
- **Resource Not Found**: Check project ID and region settings
- **Timeout**: Adjust network delay and batch size
- **Quota Exceeded**: Request API quota increase or implement retry logic

### 2. Debugging Tools
- **Logging**: Analyze detailed log files
- **API Testing**: Direct API calls using curl or gcloud commands
- **Performance Monitoring**: Track collection time and memory usage

## Performance Optimization

### 1. Improve Collection Performance
- **Batch Size Adjustment**: Set optimal batch size for environment
- **Parallel Processing**: Concurrent collection of multiple resources
- **Caching Strategy**: Cache frequently used data

### 2. Resource Usage Optimization
- **Memory Management**: Minimize memory usage through sequential processing
- **Network Optimization**: Appropriate timeout and retry settings
- **API Call Optimization**: Minimize unnecessary API calls

## Security Considerations

### 1. Authentication and Authorization
- **Service Account**: Apply principle of least privilege
- **Key Management**: Secure storage and regular rotation of key files
- **Audit Logs**: Logging for all API calls

### 2. Data Protection
- **Encryption**: Encrypt sensitive information
- **Network Security**: Secure communication through HTTPS
- **Access Control**: Use IP whitelist and VPN

## Monitoring and Operations

### 1. Performance Monitoring
- **Collection Performance**: Collection time and success rate by resource
- **System Resources**: CPU, memory, network usage
- **API Quota**: Google Cloud API usage and limits

### 2. Operations Management
- **Health Check**: Regular service status verification
- **Backup and Recovery**: Configuration and data backup strategy
- **Updates**: Regular dependency and security patches

## References

### 1. Official Documentation
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [SpaceONE Documentation](https://spaceone.io/docs)
- [Python Official Documentation](https://docs.python.org/)

### 2. Development Tools
- [Ruff (Python Linter)](https://docs.astral.sh/ruff/)
- [pytest (Testing Framework)](https://docs.pytest.org/)
- [Google Cloud Python Client](https://googleapis.dev/python/)

### 3. Community
- [SpaceONE GitHub](https://github.com/spaceone)
- [Google Cloud Community](https://cloud.google.com/community)
- [Python Community](https://www.python.org/community/)

## Contributing

### 1. How to Contribute
1. **Issue Registration**: Bug reports or feature requests
2. **Fork and Development**: Development in personal repository
3. **Pull Request**: Submit changes to main repository
4. **Code Review**: Code review and feedback from team members

### 2. Development Environment Setup
- Refer to development environment setup guide
- Write and execute test code
- Verify compliance with coding rules

### 3. Documentation Contribution
- Write and translate English documentation
- Improve code examples and usage
- Add troubleshooting guides

## License

This project is distributed under the Apache License 2.0. For details, see the [LICENSE](LICENSE) file.

## Support

### 1. Technical Support
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Refer to detailed guides for each domain
- **Community**: Utilize SpaceONE and Google Cloud communities

### 2. Contact
- **Email**: support@spaceone.dev
- **GitHub**: [SpaceONE Organization](https://github.com/spaceone)
- **Website**: [SpaceONE](https://spaceone.io/)

---

**Note**: This document is continuously updated. Check the GitHub repository for the latest information.
