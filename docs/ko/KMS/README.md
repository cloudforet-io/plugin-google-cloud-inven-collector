# Google Cloud KMS KeyRing 플러그인

이 문서는 Google Cloud Key Management Service (KMS)의 KeyRing 리소스를 수집하는 플러그인에 대한 설명입니다.

## 개요

Google Cloud KMS KeyRing 플러그인은 SpaceONE Inventory Collector의 일부로, Google Cloud의 모든 위치에 있는 KeyRing 정보를 수집합니다.

### 주요 기능

- **전체 위치 스캔**: 모든 Google Cloud 지역의 KeyRing을 자동으로 검색
- **상세 정보 수집**: KeyRing 메타데이터 및 위치 정보 포함
- **실시간 모니터링**: 생성 시간, 위치별 분류 등 상세 정보 제공

## 수집되는 정보

### KeyRing 기본 정보
- **KeyRing ID**: 고유 식별자
- **이름**: 전체 리소스 경로
- **프로젝트 ID**: 소속 프로젝트
- **생성 시간**: KeyRing 생성 시각

### 위치 정보
- **Location ID**: 지역 코드 (예: global, us-central1)
- **Location 표시명**: 사용자 친화적 지역명
- **Location 라벨**: 추가 메타데이터

## API 참조

이 플러그인은 다음 Google Cloud KMS API를 사용합니다:

### 사용된 API 엔드포인트

1. **위치 목록 조회**
   ```
   GET https://cloudkms.googleapis.com/v1/projects/{project_id}/locations
   ```

2. **KeyRing 목록 조회**
   ```
   GET https://cloudkms.googleapis.com/v1/projects/{project_id}/locations/{location}/keyRings
   ```

### 필요한 권한

플러그인이 정상적으로 작동하려면 다음 IAM 권한이 필요합니다:

- `cloudkms.keyRings.list`
- `cloudkms.locations.list`
- `resourcemanager.projects.get`

## 구현 상세

### 아키텍처

```
KMSKeyRingManager
    ↓
KMSKeyRingV1Connector
    ↓
Google Cloud KMS API
```

### 주요 컴포넌트

1. **KMSKeyRingV1Connector**
   - Google Cloud KMS API 호출 담당
   - 위치별 KeyRing 수집
   - 페이지네이션 지원

2. **KMSKeyRingManager**
   - 리소스 수집 및 처리 로직
   - 데이터 변환 및 정규화
   - 에러 처리

3. **KMSKeyRingData**
   - KeyRing 데이터 모델 정의
   - Schematics 기반 검증

### 데이터 플로우

1. **위치 검색**: 프로젝트의 모든 사용 가능한 위치 조회
2. **KeyRing 수집**: 각 위치별로 KeyRing 목록 수집
3. **데이터 처리**: 원시 데이터를 표준화된 형식으로 변환
4. **응답 생성**: SpaceONE 형식의 리소스 응답 생성

## 설정

### 프로젝트 설정

`cloud_service_conf.py`에 다음이 추가되었습니다:

```python
CLOUD_SERVICE_GROUP_MAP = {
    # ... 기존 설정 ...
    "KMS": ["KMSKeyRingManager"],
}

CLOUD_LOGGING_RESOURCE_TYPE_MAP = {
    # ... 기존 설정 ...
    "KMS": {
        "KeyRing": {
            "resource_type": "kms_keyring",
            "labels_key": "resource.labels.keyring_id",
        }
    },
}
```

### 메트릭 설정

다음 메트릭이 자동으로 수집됩니다:

- **지역별 KeyRing 수**: 각 지역별 KeyRing 개수
- **프로젝트별 KeyRing 수**: 프로젝트별 총 KeyRing 개수

## 사용법

### 테스트 실행

```bash
# 환경변수 설정
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# 테스트 실행
python test_kms.py
```

### 프로덕션 배포

1. 서비스 계정 키 준비
2. 필요한 IAM 권한 부여
3. SpaceONE Collector에 플러그인 등록
4. 수집 스케줄 설정

## 문제 해결

### 일반적인 문제

1. **권한 부족**
   - 서비스 계정에 KMS 읽기 권한 확인
   - 프로젝트 레벨에서 권한 설정 확인

2. **API 할당량 초과**
   - Google Cloud Console에서 KMS API 할당량 확인
   - 요청 빈도 조절 고려

3. **위치별 접근 제한**
   - 특정 지역의 KMS 서비스 활성화 상태 확인
   - 조직 정책으로 인한 제한 확인

### 로그 확인

상세한 로그는 다음 위치에서 확인할 수 있습니다:

```python
import logging
_LOGGER = logging.getLogger(__name__)
```

## 관련 문서

- [Google Cloud KMS API 문서](https://cloud.google.com/kms/docs/reference/rest)
- [SpaceONE Inventory Collector 가이드](../../GUIDE.md)
- [KeyRing 목록 조회 API 가이드](keyring_list_api_guide.md)
