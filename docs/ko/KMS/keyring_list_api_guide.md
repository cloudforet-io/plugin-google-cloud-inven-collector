# Google Cloud KMS: KeyRing 및 CryptoKey 목록 조회 API 가이드

이 문서는 Google Cloud Key Management Service(KMS)의 API를 사용하여 KeyRing 및 CryptoKey 목록을 조회하는 방법을 안내합니다.

## 🚀 최적화된 Location 검색 옵션

KMS KeyRing 수집 시 효율적인 location 검색을 위한 다양한 옵션을 제공합니다:

### 옵션 1: 특정 Location만 검색
```json
{
  "options": {
    "cloud_service_types": ["KMS"],
    "kms_locations": ["global", "us-central1", "asia-northeast3"]
  }
}
```

### 옵션 2: 최적화된 검색 (기본값)
```json
{
  "options": {
    "cloud_service_types": ["KMS"],
    "kms_optimize_search": true
  }
}
```
일반적으로 사용되는 location을 우선적으로 검색합니다.

### 옵션 3: 모든 Location 검색
```json
{
  "options": {
    "cloud_service_types": ["KMS"],
    "kms_optimize_search": false
  }
}
```

---

## 1. KeyRing 목록 조회 (`projects.locations.keyRings.list`)

이 API를 사용하면 특정 위치에 있는 모든 키링(KeyRing)의 목록을 가져올 수 있습니다.

### 1.1. 개요

- **목적**: 지정된 위치(location)에 있는 모든 키링(KeyRing)의 목록을 조회합니다.
- **엔드포인트**: `projects.locations.keyRings.list`

### 1.2. HTTP 요청

`GET` 메서드를 사용하여 다음 URL 형식으로 요청을 보냅니다.

```
GET https://cloudkms.googleapis.com/v1/{parent=projects/*/locations/*}/keyRings
```

### 1.3. 매개변수

#### 경로 매개변수

| 이름     | 타입   | 설명                                            | 필수 |
| :------- | :----- | :---------------------------------------------- | :--- |
| `parent` | string | 키링이 속한 위치의 리소스 이름입니다. <br> 형식: `projects/{프로젝트_ID}/locations/{위치}` | 예   |

#### 쿼리 매개변수

| 이름          | 타입   | 설명                                                                                             | 필수 |
| :------------ | :----- | :----------------------------------------------------------------------------------------------- | :--- |
| `pageSize`    | integer| 한 번의 응답에 포함할 키링의 최대 개수입니다. 지정하지 않으면 서버 기본값이 사용됩니다.           | 아니요 |
| `pageToken`   | string | 이전 목록 요청에서 반환된 `nextPageToken` 값을 사용하여 결과의 다음 페이지를 가져옵니다.         | 아니요 |
| `filter`      | string | 지정한 필터와 일치하는 리소스만 응답에 포함시킵니다. (예: `name:my-keyring`)                      | 아니요 |
| `orderBy`     | string | 결과를 정렬할 기준을 지정합니다. (예: `name asc`)                                                | 아니요 |

### 1.4. 요청 본문

요청 본문은 비어 있어야 합니다.

### 1.5. 응답 본문

요청이 성공하면 다음과 같은 JSON 형식의 응답 본문을 받게 됩니다.

```json
{
  "keyRings": [
    {
      "name": "projects/your-project-id/locations/global/keyRings/my-key-ring-1",
      "createTime": "2024-01-01T12:34:56.789Z"
    },
    {
      "name": "projects/your-project-id/locations/global/keyRings/my-key-ring-2",
      "createTime": "2024-01-02T12:34:56.789Z"
    }
  ],
  "nextPageToken": "...",
  "totalSize": 2
}
```

- `keyRings[]`: `KeyRing` 객체의 목록입니다.
- `nextPageToken`: 결과의 다음 페이지를 가져오는 데 사용할 수 있는 토큰입니다. 모든 결과가 반환되면 이 필드는 비어 있습니다.
- `totalSize`: 쿼리와 일치하는 총 키링의 수입니다.

### 1.6. 예시 (cURL)

다음은 `curl`을 사용하여 API를 호출하는 예시입니다.

```bash
# YOUR_PROJECT_ID와 YOUR_LOCATION을 실제 값으로 변경해야 합니다.
# YOUR_ACCESS_TOKEN은 gcloud auth print-access-token 명령어로 얻을 수 있습니다.

cURL "https://cloudkms.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/keyRings" \
  --header "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --header "Content-Type: application/json"
```

---

## 2. CryptoKey 목록 조회 (`projects.locations.keyRings.cryptoKeys.list`)

이 API를 사용하면 특정 키링(KeyRing)에 속한 모든 암호화 키(CryptoKey)의 목록을 가져올 수 있습니다.

### 2.1. 개요

- **목적**: 지정된 키링(KeyRing)에 있는 모든 암호화 키(CryptoKey)의 목록을 조회합니다.
- **엔드포인트**: `projects.locations.keyRings.cryptoKeys.list`

### 2.2. HTTP 요청

`GET` 메서드를 사용하여 다음 URL 형식으로 요청을 보냅니다.

```
GET https://cloudkms.googleapis.com/v1/{parent=projects/*/locations/*/keyRings/*}/cryptoKeys
```

### 2.3. 매개변수

#### 경로 매개변수

| 이름     | 타입   | 설명                                                                                             | 필수 |
| :------- | :----- | :----------------------------------------------------------------------------------------------- | :--- |
| `parent` | string | 암호화 키가 속한 키링의 리소스 이름입니다. <br> 형식: `projects/{프로젝트_ID}/locations/{위치}/keyRings/{키링_이름}` | 예   |

#### 쿼리 매개변수

| 이름          | 타입    | 설명                                                                                             | 필수 |
| :------------ | :------ | :----------------------------------------------------------------------------------------------- | :--- |
| `pageSize`    | integer | 한 번의 응답에 포함할 암호화 키의 최대 개수입니다. 지정하지 않으면 서버 기본값이 사용됩니다.       | 아니요 |
| `pageToken`   | string  | 이전 목록 요청에서 반환된 `nextPageToken` 값을 사용하여 결과의 다음 페이지를 가져옵니다.         | 아니요 |
| `versionView` | enum    | 응답에 포함할 기본 `CryptoKeyVersion`의 필드를 지정합니다.                                       | 아니요 |
| `filter`      | string  | 지정한 필터와 일치하는 리소스만 응답에 포함시킵니다.                                             | 아니요 |
| `orderBy`     | string  | 결과를 정렬할 기준을 지정합니다.                                                                 | 아니요 |

### 2.4. 요청 본문

요청 본문은 비어 있어야 합니다.

### 2.5. 응답 본문

요청이 성공하면 다음과 같은 JSON 형식의 응답 본문을 받게 됩니다.

```json
{
  "cryptoKeys": [
    {
      "name": "projects/your-project-id/locations/global/keyRings/my-key-ring/cryptoKeys/my-crypto-key-1",
      "primary": {
        "name": "projects/your-project-id/locations/global/keyRings/my-key-ring/cryptoKeys/my-crypto-key-1/cryptoKeyVersions/1",
        "state": "ENABLED"
      },
      "purpose": "ENCRYPT_DECRYPT",
      "createTime": "2024-01-01T12:34:56.789Z",
      "nextRotationTime": "2025-01-01T12:34:56.789Z",
      "versionTemplate": {
        "protectionLevel": "SOFTWARE",
        "algorithm": "GOOGLE_SYMMETRIC_ENCRYPTION"
      }
    }
  ],
  "nextPageToken": "...",
  "totalSize": 1
}
```

- `cryptoKeys[]`: `CryptoKey` 객체의 목록입니다.
- `nextPageToken`: 결과의 다음 페이지를 가져오는 데 사용할 수 있는 토큰입니다. 모든 결과가 반환되면 이 필드는 비어 있습니다.
- `totalSize`: 쿼리와 일치하는 총 암호화 키의 수입니다.

### 2.6. 예시 (cURL)

다음은 `curl`을 사용하여 API를 호출하는 예시입니다.

```bash
# YOUR_PROJECT_ID, YOUR_LOCATION, YOUR_KEYRING_NAME을 실제 값으로 변경해야 합니다.
# YOUR_ACCESS_TOKEN은 gcloud auth print-access-token 명령어로 얻을 수 있습니다.

cURL "https://cloudkms.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/keyRings/YOUR_KEYRING_NAME/cryptoKeys" \
  --header "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --header "Content-Type: application/json"
```