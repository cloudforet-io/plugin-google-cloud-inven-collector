# Google Cloud Inventory Collector 문서

## 개요

이 문서는 SpaceONE Google Cloud Inventory Collector 플러그인에서 지원하는 Google Cloud 서비스들의 리소스 수집 방법과 구현 가이드를 제공합니다.

## 지원 서비스

### 1. App Engine
- **설명**: Google Cloud의 완전 관리형 서버리스 플랫폼
- **수집 리소스**: Application, Service, Version, Instance
- **API 버전**: v1, v1beta (하위 호환성)
- **문서**: [App Engine 가이드](./prd/app_engine/README.md)

### 2. Kubernetes Engine (GKE)
- **설명**: Google Cloud의 관리형 Kubernetes 클러스터 서비스
- **수집 리소스**: Cluster, Node Pool, Node, Node Group
- **API 버전**: v1, v1beta (하위 호환성)
- **문서**: [Kubernetes Engine 가이드](./prd/kubernetes_engine/README.md)

### 3. 기타 서비스들
- Compute Engine
- Cloud Storage
- Cloud SQL
- BigQuery
- Cloud Functions
- Cloud Run
- Firebase
- KMS
- Dataproc
- Cloud Build
- Filestore
- Firestore
- Datastore
- Pub/Sub
- Networking
- Batch
- Storage Transfer
- Recommender

## 문서 구조

```
docs/ko/
├── README.md                           # 이 파일
├── guide/                             # 일반 가이드
├── development/                       # 개발 가이드
└── prd/                              # 제품 요구사항 정의서
    ├── app_engine/                    # App Engine 도메인
    │   ├── README.md                  # 종합 가이드
    │   ├── API_Reference.md           # API 참조
    │   └── Implementation_Guide.md    # 구현 가이드
    ├── kubernetes_engine/             # Kubernetes Engine 도메인
    │   ├── README.md                  # 종합 가이드
    │   ├── API_Reference.md           # API 참조
    │   └── Implementation_Guide.md    # 구현 가이드
    ├── storage_transfer/              # Storage Transfer 도메인
    ├── firestore/                     # Firestore 도메인
    ├── kms/                           # KMS 도메인
    ├── datastore/                     # Datastore 도메인
    ├── filestore/                     # Filestore 도메인
    ├── dataproc/                      # Dataproc 도메인
    ├── cloud_run/                     # Cloud Run 도메인
    └── cloud_build/                   # Cloud Build 도메인
```

## 주요 기능

### 1. 리소스 수집
- **계층적 수집**: Application → Service → Version → Instance 구조
- **배치 처리**: 대량 데이터의 효율적인 처리
- **병렬 처리**: 여러 리소스의 동시 수집
- **캐싱**: 반복 API 호출 최소화

### 2. 에러 처리
- **재시도 로직**: 일시적 오류에 대한 자동 재시도
- **상세한 에러 메시지**: 문제 해결을 위한 명확한 정보 제공
- **로깅**: 모든 작업에 대한 상세한 로그 기록

### 3. 성능 최적화
- **타임아웃 관리**: API 호출별 적절한 타임아웃 설정
- **메모리 효율성**: 순차 처리로 메모리 사용량 최소화
- **API 할당량 관리**: 할당량 초과 방지 및 최적화

### 4. 모니터링
- **성능 메트릭**: 수집 시간, 오류율 등 성능 지표
- **상태 추적**: 리소스별 상태 및 건강도 모니터링
- **헬스 체크**: 서비스 상태 실시간 확인

## 아키텍처

### Service-Manager-Connector 구조
```
Service Layer (API 엔드포인트)
    ↓
Manager Layer (비즈니스 로직)
    ↓
Connector Layer (Google Cloud API 연동)
```

### 리소스 수집 플로우
1. **초기화**: 인증 정보 및 설정 로드
2. **수집**: API를 통한 리소스 정보 조회
3. **처리**: 메타데이터 추가 및 데이터 정제
4. **검증**: 데이터 무결성 및 관계 검사
5. **저장**: SpaceONE 인벤토리에 리소스 저장

## 시작하기

### 1. 사전 요구사항
- Python 3.8+
- Google Cloud 프로젝트
- Service Account 키 파일
- 필요한 API 활성화

### 2. 설치 및 설정
```bash
# 저장소 클론
git clone <repository-url>
cd plugin-google-cloud-inven-collector

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
export GOOGLE_CLOUD_PROJECT_ID="your-project-id"
```

### 3. 실행
```bash
# 기본 수집 실행
python -m spaceone.inventory.service.collector_service

# 특정 서비스만 수집
python -m spaceone.inventory.service.collector_service --service app_engine
```

## 개발 가이드

### 1. 새로운 서비스 추가
1. **Connector 구현**: Google Cloud API 연동
2. **Manager 구현**: 비즈니스 로직 및 데이터 처리
3. **Model 정의**: 데이터 구조 및 검증
4. **테스트 작성**: 단위 및 통합 테스트
5. **문서화**: API 참조 및 구현 가이드

### 2. 코딩 규칙
- **이름 규칙**: snake_case (변수, 함수), PascalCase (클래스)
- **문서화**: Google 스타일 Docstring (한국어)
- **에러 처리**: 구체적인 예외 처리 및 로깅
- **테스트**: 모든 기능에 대한 테스트 코드 작성

### 3. 품질 보증
- **린팅**: Ruff를 통한 코드 스타일 검사
- **포맷팅**: 자동 코드 포맷팅 적용
- **테스트**: pytest를 통한 테스트 실행
- **커버리지**: 코드 커버리지 80% 이상 유지

## 문제 해결

### 1. 일반적인 문제들
- **권한 오류**: IAM 역할 및 API 활성화 확인
- **리소스 없음**: 프로젝트 ID 및 리전 설정 확인
- **타임아웃**: 네트워크 지연 및 배치 크기 조정
- **할당량 초과**: API 할당량 증가 요청 또는 재시도 로직 구현

### 2. 디버깅 도구
- **로깅**: 상세한 로그 파일 분석
- **API 테스트**: curl 또는 gcloud 명령어로 직접 API 호출
- **성능 모니터링**: 수집 시간 및 메모리 사용량 추적

## 성능 최적화

### 1. 수집 성능 향상
- **배치 크기 조정**: 환경에 맞는 최적 배치 크기 설정
- **병렬 처리**: 여러 리소스의 동시 수집
- **캐싱 전략**: 자주 사용되는 데이터의 캐싱

### 2. 리소스 사용량 최적화
- **메모리 관리**: 순차 처리로 메모리 사용량 최소화
- **네트워크 최적화**: 적절한 타임아웃 및 재시도 설정
- **API 호출 최적화**: 불필요한 API 호출 최소화

## 보안 고려사항

### 1. 인증 및 권한
- **Service Account**: 최소 권한 원칙 적용
- **키 관리**: 키 파일의 안전한 보관 및 정기 교체
- **감사 로그**: 모든 API 호출에 대한 로깅

### 2. 데이터 보호
- **암호화**: 민감한 정보의 암호화 처리
- **네트워크 보안**: HTTPS를 통한 안전한 통신
- **접근 제어**: IP 화이트리스트 및 VPN 사용

## 모니터링 및 운영

### 1. 성능 모니터링
- **수집 성능**: 리소스별 수집 시간 및 성공률
- **시스템 리소스**: CPU, 메모리, 네트워크 사용량
- **API 할당량**: Google Cloud API 사용량 및 제한

### 2. 운영 관리
- **헬스 체크**: 정기적인 서비스 상태 확인
- **백업 및 복구**: 설정 및 데이터 백업 전략
- **업데이트**: 정기적인 의존성 및 보안 패치

## 참고 자료

### 1. 공식 문서
- [Google Cloud 문서](https://cloud.google.com/docs)
- [SpaceONE 문서](https://spaceone.io/docs)
- [Python 공식 문서](https://docs.python.org/)

### 2. 개발 도구
- [Ruff (Python 린터)](https://docs.astral.sh/ruff/)
- [pytest (테스트 프레임워크)](https://docs.pytest.org/)
- [Google Cloud Python 클라이언트](https://googleapis.dev/python/)

### 3. 커뮤니티
- [SpaceONE GitHub](https://github.com/spaceone)
- [Google Cloud Community](https://cloud.google.com/community)
- [Python 커뮤니티](https://www.python.org/community/)

## 기여하기

### 1. 기여 방법
1. **Issue 등록**: 버그 리포트 또는 기능 요청
2. **Fork 및 개발**: 개인 저장소에서 개발
3. **Pull Request**: 메인 저장소로 변경사항 제출
4. **코드 리뷰**: 팀원들의 코드 검토 및 피드백

### 2. 개발 환경 설정
- 개발 환경 설정 가이드 참조
- 테스트 코드 작성 및 실행
- 코딩 규칙 준수 확인

### 3. 문서 기여
- 한국어 문서 작성 및 번역
- 코드 예시 및 사용법 개선
- 문제 해결 가이드 추가

## 라이선스

이 프로젝트는 Apache License 2.0 하에 배포됩니다. 자세한 내용은 [LICENSE](../LICENSE) 파일을 참조하세요.

## 지원

### 1. 기술 지원
- **GitHub Issues**: 버그 리포트 및 기능 요청
- **문서**: 각 도메인별 상세 가이드 참조
- **커뮤니티**: SpaceONE 및 Google Cloud 커뮤니티 활용

### 2. 연락처
- **이메일**: support@spaceone.dev
- **GitHub**: [SpaceONE Organization](https://github.com/spaceone)
- **웹사이트**: [SpaceONE](https://spaceone.io/)

---

**참고**: 이 문서는 지속적으로 업데이트됩니다. 최신 정보는 GitHub 저장소를 확인하세요.
