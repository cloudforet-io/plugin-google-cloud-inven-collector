# Google Cloud KMS: KeyRing 및 CryptoKey 목록 조회 API 가이드

이 문서는 Google Cloud Key Management Service(KMS)의 API를 사용하여 KeyRing, CryptoKey 및 CryptoKeyVersion 목록을 조회하는 방법을 안내합니다.

## 🚀 KMS Location 검색 옵션

KMS KeyRing 수집 시 location 검색 방법을 선택할 수 있습니다:

### 옵션 1: 특정 Location만 검색 🎯 (권장)
```json
{
  "options": {
    "cloud_service_types": ["KMS"],
    "kms_locations": ["global", "us-central1", "asia-northeast3"]
  }
}
```
**가장 빠른 방법**: 알고 있는 특정 location들만 검색합니다.

### 옵션 2: 모든 Location 검색 🌐
```json
{
  "options": {
    "cloud_service_types": ["KMS"]
  }
}
```
모든 사용 가능한 location을 검색합니다 (시간이 오래 걸림).

### 💡 사용 권장사항

**대부분의 경우** (가장 빠름):
```json
"kms_locations": ["global", "asia-northeast3"]  // 글로벌 + 서울
```

**전체 검색이 필요한 경우**:
```json
// kms_locations를 지정하지 않으면 모든 location 검색
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

---

## 3. CryptoKeyVersion 목록 조회 (`projects.locations.keyRings.cryptoKeys.cryptoKeyVersions.list`)

이 API를 사용하면 특정 암호화 키(CryptoKey)에 속한 모든 키 버전(CryptoKeyVersion)의 목록을 가져올 수 있습니다.

### 3.1. 개요

- **목적**: 지정된 암호화 키(CryptoKey)에 있는 모든 키 버전(CryptoKeyVersion)의 목록을 조회합니다.
- **엔드포인트**: `projects.locations.keyRings.cryptoKeys.cryptoKeyVersions.list`
- **참조**: [Google Cloud KMS API 문서](https://cloud.google.com/kms/docs/reference/rest/v1/projects.locations.keyRings.cryptoKeys.cryptoKeyVersions/list)

### 3.2. HTTP 요청

`GET` 메서드를 사용하여 다음 URL 형식으로 요청을 보냅니다.

```
GET https://cloudkms.googleapis.com/v1/{parent=projects/*/locations/*/keyRings/*/cryptoKeys/*}/cryptoKeyVersions
```

### 3.3. 매개변수

#### 경로 매개변수

| 이름     | 타입   | 설명                                                                                             | 필수 |
| :------- | :----- | :----------------------------------------------------------------------------------------------- | :--- |
| `parent` | string | 키 버전이 속한 암호화 키의 리소스 이름입니다. <br> 형식: `projects/{프로젝트_ID}/locations/{위치}/keyRings/{키링_이름}/cryptoKeys/{암호화키_이름}` | 예   |

#### 쿼리 매개변수

| 이름          | 타입    | 설명                                                                                             | 필수 |
| :------------ | :------ | :----------------------------------------------------------------------------------------------- | :--- |
| `pageSize`    | integer | 한 번의 응답에 포함할 키 버전의 최대 개수입니다. 지정하지 않으면 서버 기본값이 사용됩니다.         | 아니요 |
| `pageToken`   | string  | 이전 목록 요청에서 반환된 `nextPageToken` 값을 사용하여 결과의 다음 페이지를 가져옵니다.         | 아니요 |
| `view`        | enum    | 응답에 포함할 필드를 지정합니다. ([CryptoKeyVersionView](/kms/docs/reference/rest/v1/CryptoKeyVersionView)) | 아니요 |
| `filter`      | string  | 지정한 필터와 일치하는 리소스만 응답에 포함시킵니다. [정렬 및 필터링 가이드](https://cloud.google.com/kms/docs/sorting-and-filtering) 참조 | 아니요 |
| `orderBy`     | string  | 결과를 정렬할 기준을 지정합니다. [정렬 및 필터링 가이드](https://cloud.google.com/kms/docs/sorting-and-filtering) 참조 | 아니요 |

### 3.4. 요청 본문

요청 본문은 비어 있어야 합니다.

### 3.5. 응답 본문

요청이 성공하면 다음과 같은 JSON 형식의 응답 본문을 받게 됩니다.

```json
{
  "cryptoKeyVersions": [
    {
      "name": "projects/your-project-id/locations/global/keyRings/my-key-ring/cryptoKeys/my-crypto-key/cryptoKeyVersions/1",
      "state": "ENABLED",
      "createTime": "2024-01-01T12:34:56.789Z",
      "protectionLevel": "SOFTWARE",
      "algorithm": "GOOGLE_SYMMETRIC_ENCRYPTION",
      "generateTime": "2024-01-01T12:34:56.789Z"
    },
    {
      "name": "projects/your-project-id/locations/global/keyRings/my-key-ring/cryptoKeys/my-crypto-key/cryptoKeyVersions/2",
      "state": "DISABLED",
      "createTime": "2024-01-02T12:34:56.789Z",
      "protectionLevel": "SOFTWARE",
      "algorithm": "GOOGLE_SYMMETRIC_ENCRYPTION",
      "generateTime": "2024-01-02T12:34:56.789Z"
    }
  ],
  "nextPageToken": "...",
  "totalSize": 2
}
```

- `cryptoKeyVersions[]`: `CryptoKeyVersion` 객체의 목록입니다.
- `nextPageToken`: 결과의 다음 페이지를 가져오는 데 사용할 수 있는 토큰입니다. 모든 결과가 반환되면 이 필드는 비어 있습니다.
- `totalSize`: 쿼리와 일치하는 총 키 버전의 수입니다.

### 3.6. CryptoKeyVersion 상태

CryptoKeyVersion은 다음과 같은 상태를 가질 수 있습니다:

- `ENABLED`: 활성화된 상태로 암호화/복호화 작업에 사용 가능
- `DISABLED`: 비활성화된 상태로 암호화/복호화 작업에 사용 불가
- `DESTROYED`: 파괴된 상태로 복구 불가
- `DESTROY_SCHEDULED`: 파괴 예정 상태
- `PENDING_GENERATION`: 생성 대기 중
- `PENDING_IMPORT`: 가져오기 대기 중
- `PENDING_EXTERNAL_DESTRUCTION`: 외부 파괴 대기 중
- `EXTERNAL_DESTRUCTION_FAILED`: 외부 파괴 실패

### 3.7. 예시 (cURL)

다음은 `curl`을 사용하여 API를 호출하는 예시입니다.

```bash
# YOUR_PROJECT_ID, YOUR_LOCATION, YOUR_KEYRING_NAME, YOUR_CRYPTO_KEY_NAME을 실제 값으로 변경해야 합니다.
# YOUR_ACCESS_TOKEN은 gcloud auth print-access-token 명령어로 얻을 수 있습니다.

curl "https://cloudkms.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/keyRings/YOUR_KEYRING_NAME/cryptoKeys/YOUR_CRYPTO_KEY_NAME/cryptoKeyVersions" \
  --header "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --header "Content-Type: application/json"
```

### 3.8. 필터링 예시

특정 상태의 키 버전만 조회하려면 `filter` 매개변수를 사용할 수 있습니다:

```bash
# 활성화된 키 버전만 조회
curl "https://cloudkms.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/keyRings/YOUR_KEYRING_NAME/cryptoKeys/YOUR_CRYPTO_KEY_NAME/cryptoKeyVersions?filter=state:ENABLED" \
  --header "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --header "Content-Type: application/json"

# 특정 보호 수준의 키 버전만 조회
curl "https://cloudkms.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/keyRings/YOUR_KEYRING_NAME/cryptoKeys/YOUR_CRYPTO_KEY_NAME/cryptoKeyVersions?filter=protectionLevel:SOFTWARE" \
  --header "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --header "Content-Type: application/json"
```

---

## 4. 권한 요구사항

KMS API를 사용하기 위해서는 다음 IAM 권한이 필요합니다:

### 4.1. 필수 권한

- `cloudkms.keyRings.list` - KeyRing 목록 조회
- `cloudkms.cryptoKeys.list` - CryptoKey 목록 조회  
- `cloudkms.cryptoKeyVersions.list` - CryptoKeyVersion 목록 조회

### 4.2. OAuth 스코프

다음 OAuth 스코프 중 하나가 필요합니다:

- `https://www.googleapis.com/auth/cloudkms`
- `https://www.googleapis.com/auth/cloud-platform`

### 4.3. 서비스 계정 설정

SpaceONE 플러그인에서 사용하는 서비스 계정에 다음 역할을 부여해야 합니다:

- `Cloud KMS Admin` (전체 관리)
- 또는 `Cloud KMS Viewer` (읽기 전용)

---

## 5. 에러 처리

### 5.1. 일반적인 에러 코드

| HTTP 상태 코드 | 에러 메시지 | 설명 |
| :------------ | :---------- | :--- |
| 400 | `INVALID_ARGUMENT` | 잘못된 매개변수 |
| 401 | `UNAUTHENTICATED` | 인증 실패 |
| 403 | `PERMISSION_DENIED` | 권한 부족 |
| 404 | `NOT_FOUND` | 리소스를 찾을 수 없음 |
| 429 | `RESOURCE_EXHAUSTED` | 요청 한도 초과 |

### 5.2. 재시도 전략

API 호출 시 다음 재시도 전략을 권장합니다:

- **지수 백오프**: 1초, 2초, 4초, 8초 간격으로 재시도
- **최대 재시도**: 3-5회
- **429 에러**: Rate limiting으로 인한 경우 더 긴 대기 시간 적용

---

## 6. 성능 최적화

### 6.1. 페이지네이션

대량의 데이터를 조회할 때는 페이지네이션을 활용하세요:

```bash
# 첫 번째 페이지
curl "https://cloudkms.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/keyRings?pageSize=100"

# 다음 페이지 (nextPageToken 사용)
curl "https://cloudkms.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/keyRings?pageSize=100&pageToken=NEXT_PAGE_TOKEN"
```

### 6.2. 필터링 활용

필요한 데이터만 조회하여 성능을 향상시킬 수 있습니다:

```bash
# 특정 이름 패턴의 KeyRing만 조회
curl "https://cloudkms.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/keyRings?filter=name:my-keyring*"

# 활성화된 CryptoKey만 조회
curl "https://cloudkms.googleapis.com/v1/projects/YOUR_PROJECT_ID/locations/YOUR_LOCATION/keyRings/YOUR_KEYRING_NAME/cryptoKeys?filter=primary.state:ENABLED"
```

---

## 7. 참고 자료

- [Google Cloud KMS API 개요](https://cloud.google.com/kms/docs/reference/rest)
- [KMS REST API v1 참조](https://cloud.google.com/kms/docs/reference/rest/v1)
- [IAM 및 KMS 권한](https://cloud.google.com/kms/docs/iam)
- [정렬 및 필터링 가이드](https://cloud.google.com/kms/docs/sorting-and-filtering)
- [SpaceONE KMS 플러그인 가이드](../GUIDE.md)