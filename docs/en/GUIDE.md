## Overview

To register a Google Cloud service account in Cloudforet, you need configuration information for **[Project ID]** and **[google_oauth2_credentials]**.

> 💡 Before starting this setup guide, please create **at least one project**.
For project creation instructions, refer to the [Google Cloud Documentation](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project).

<img src="./GUIDE-img/overview(h2)-1.png" width="80%" height="80%">
<img src="./GUIDE-img/overview(h2)-2.png" width="80%" height="80%">

This setup guide will explain in detail what the two configuration items mentioned above mean and where to obtain them.

<br>

### Project ID

A unique string used to distinguish projects in Google Cloud.

For a detailed explanation of **Project ID**, see the [Google Cloud Documentation](https://cloud.google.com/resource-manager/docs/creating-managing-projects#before_you_begin).

<br>

### **google_oauth2_credentials**

The **[google_oauth2_credentials]** method provides **credentials** based on OAuth 2.0.

This allows access to resources on behalf of the user (resource owner).

For a detailed explanation of Google API authentication methods, see the [Google Cloud Documentation](https://developers.google.com/identity/protocols/oauth2?hl=en).

<br>
We've briefly covered two concepts.

Now, let's delve into **how to actually obtain configuration information** in the following steps.

<br>

## Overall Flow

CloudFore supports the **[google_oauth2_credentials]** method based on OAuth 2.0 for Google Cloud integration.
Using **[google_oauth2_credentials]** requires the following configuration information:

- **Client Email**
- **Client ID**
- **Private Key**
- **Private Key ID**
- **Project ID**
- **client_x509_cert_url**

To obtain the above information, follow the steps below.

1. [Create a Google Cloud Service Account](#1-Create-Google-Cloud-Service-Account)

2. [Create a Role](#2-Create-Role)

3. [Create an Additional Role](#3-Create-Additional-Role)

4. [Create an Authentication Key](#4-Create-Authentication-Key)

5. [Register a SpaceONE Service Account](#5-Register-SpaceONE-Service-Account)

<br>
<br>

## 1. Create a Google Cloud Service Account
A [Service Account](https://cloud.google.com/iam/docs/service-accounts)(Service Account) is an account that can access Google Cloud resources.

Cloud Forest collects resource information using the service account provided by Google Cloud.

>💡 **Cloud Forest Service Account** and **Google Cloud Service Account** are different concepts.
> Also, there's a difference between a service account and a user account in Google Cloud.
> For more information, see the [Google Cloud Documentation](https://cloud.google.com/iam/docs/service-accounts#differences_between_a_service_account_and_a_user_account).

<br>

(1-1) [Sign in to Google Cloud](https://cloud.google.com/gcp/?hl=en) > [IAM Console](https://console.cloud.google.com/projectselector2/iam-admin/iam?supportedpurview=organizationId,folder,project&orgonly=true) > Click on your project.

(1-2) From the [IAM & Admin > Service Accounts] menu, click [Create Service Account].

<img src="./GUIDE-img/create-gcp-service-account(h2)-1.png" width="80%" height="80%">

(1-3) Enter the service account details.

(1-4) Click the [Create and Continue] button.

<img src="./GUIDE-img/create-gcp-service-account(h2)-2.png" width="80%" height="80%">

<br>
<br>

## 2. Create a Role and Add it to the Service Account

[Roles](https://cloud.google.com/iam/docs/understanding-roles#basic) contain permissions to perform specific actions on Google Cloud resources.

Assigning a role to a service account grants it the permissions it contains.

You must set the appropriate permissions for the service account so that the Google Cloud plugin can collect resource information.
This collector plugin does not require any permissions other than read access.

The following is a list of permissions required to collect Google Cloud services and resources that the collector plugin can collect.
The Google collector plugin collects data from eight services, and roles with the necessary permissions must be created.

The required permissions for each service correspond to the Required Roles in the table. Except for Storage Viewer (Custom), each role corresponds to a default role provided by Google. (Role names in Korean)

<br>

| No | Service | Required Role | URL |
|----|----------------|-------------------------------------|--------------------------------------------------------------------------------------|
| 1 | Compute Engine | Compute Viewer | https://github.com/cloudforet-io/plugin-google-cloud-inven-collector/#compute-engine |
| 2 | Networking | Compute Viewer | https://github.com/cloudforet-io/plugin-google-cloud-inven-collector/#networking |
| 3 | Cloud SQL | Cloud SQL Viewer | https://github.com/cloudforet-io/plugin-google-cloud-inven-collector/#cloud-sql |
| 4 | Storage | Storage Viewer (Custom), Environment and Storage Object Viewer | https://github.com/cloudforet-io/plugin-google-cloud-inven-collector/#storage |
| 5 | BigQuery | BigQuery Resource Viewer | https://github.com/cloudforet-io/plugin-google-cloud-inven-collector/#bigquery |
| 6 | Cloud Pub/Sub | Publish/Subscribe Viewer | https://github.com/cloudforet-io/plugin-google-cloud-inven-collector/tree/master#pubsub |
| 7 | Cloud Functions | Cloud Function Viewer | https://github.com/cloudforet-io/plugin-google-cloud-inven-collector/tree/master#Functions |
| 8 | Recommender | Cloud Asset Viewer, Recommender Viewer | https://github.com/cloudforet-io/plugin-google-cloud-inven-collector/tree/master#Recommender |

First, let's add the required custom roles.

Next, we'll add the roles to the service account along with the default roles.

### Creating a Custom Role

Since the Storage Viewer is not supported as a default role, you must create a custom role.

The table below lists the permissions required for the Storage Viewer (Custom).
