# Google Cloud Networking 인벤토리 수집 제품 요구사항 정의서 (PRD)

## 1. 비즈니스 요구사항 (Business Requirements)

### 1.1. 목적 (Purpose)
SpaceONE 인벤토리 플랫폼에서 Google Cloud Networking 리소스를 자동으로 수집, 분류, 모니터링하여 네트워크 인프라 관리 효율성을 극대화합니다. 네트워크 관리팀과 보안팀이 VPC, 서브넷, 방화벽, 로드밸런서 등의 상태와 구성을 통합적으로 관리할 수 있도록 지원합니다.

### 1.2. 사용자 스토리 (User Stories)
- **네트워크 관리자**: 모든 프로젝트의 네트워크 리소스 현황을 한눈에 파악하고 네트워크 토폴로지 및 보안 설정을 최적화
- **보안 엔지니어**: 방화벽 규칙과 라우팅 테이블을 모니터링하여 보안 취약점을 사전에 감지
- **팀 리더**: 팀별 네트워크 리소스 사용량과 비용을 추적하여 예산 관리 최적화

### 1.3. 수용 기준 (Acceptance Criteria)
**P0 (필수)**:
- 모든 VPC 네트워크 및 서브넷 정보 수집 (100% 정확도)
- 방화벽 규칙 및 라우팅 테이블 정보 연계
- 외부 IP 주소 및 로드밸런서 정보 수집

**P1 (중요)**:
- VPN 게이트웨이 및 피어링 연결 정보
- 네트워크 보안 정책 및 접근 제어
- 다중 프로젝트 및 리전 병렬 수집

**P2 (선택)**:
- 네트워크 성능 메트릭 연계
- 네트워크 토폴로지 시각화

## 2. API 인터페이스 (API Interface)

### 2.1. 수집 엔드포인트 (Collection Endpoints)

#### 2.1.1. Networking 리소스 수집 API
- **경로**: Internal API (플러그인 인터페이스)
- **메서드**: `collect_cloud_service()`
- **인증**: Google Cloud Service Account 키 기반
- **Rate Limit**: Google Cloud API 할당량 (분당 2000 요청)
- **Request 스키마**:
  ```json
  {
    "secret_data": {
      "project_id": "string",
      "type": "service_account",
      "private_key": "string",
      "client_email": "string"
    },
    "options": {
      "region_filter": "optional array"
    }
  }
  ```

## 3. 데이터 & 아키텍처 (Data & Architecture)

### 3.1. 데이터 모델 (Data Models)

#### 3.1.1. 주요 엔터티
- **VPCNetwork**: VPC 네트워크 메인 엔터티
  - `network_id`: 네트워크 식별자
  - `name`: 네트워크 이름
  - `description`: 설명
  - `routing_config`: 라우팅 구성
  - `auto_create_subnetworks`: 자동 서브넷 생성 여부
  - `mtu`: 최대 전송 단위
  - `peerings`: 피어링 연결 목록
  - `creation_timestamp`: 생성 시간

- **VPCSubnet**: 서브넷 엔터티
  - `subnet_id`: 서브넷 식별자
  - `name`: 서브넷 이름
  - `network`: 상위 네트워크
  - `ip_cidr_range`: IP CIDR 범위
  - `region`: 리전
  - `gateway_address`: 게이트웨이 주소
  - `private_ip_google_access`: 프라이빗 Google 액세스 여부
  - `secondary_ip_ranges`: 보조 IP 범위
  - `log_config`: 플로우 로그 구성

- **Firewall**: 방화벽 규칙 엔터티
  - `firewall_id`: 방화벽 식별자
  - `name`: 방화벽 이름
  - `description`: 설명
  - `network`: 대상 네트워크
  - `direction`: 방향 (INGRESS, EGRESS)
  - `priority`: 우선순위
  - `source_ranges`: 소스 IP 범위
  - `target_tags`: 대상 태그
  - `allowed`: 허용 규칙
  - `denied`: 거부 규칙
  - `disabled`: 비활성화 여부

- **ExternalIPAddress**: 외부 IP 주소 엔터티
  - `address_id`: 주소 식별자
  - `name`: 주소 이름
  - `address`: IP 주소
  - `address_type`: 주소 타입 (EXTERNAL, INTERNAL)
  - `status`: 상태 (RESERVED, IN_USE)
  - `region`: 리전
  - `users`: 사용자 목록
  - `network_tier`: 네트워크 티어

- **LoadBalancer**: 로드밸런서 엔터티
  - `lb_id`: 로드밸런서 식별자
  - `name`: 로드밸런서 이름
  - `description`: 설명
  - `ip_address`: IP 주소
  - `port_range`: 포트 범위
  - `target`: 대상 (백엔드 서비스, 인스턴스 그룹 등)
  - `protocol`: 프로토콜 (TCP, UDP, HTTP, HTTPS)
  - `load_balancing_scheme`: 로드밸런싱 스킴

- **Route**: 라우팅 테이블 엔터티
  - `route_id`: 라우트 식별자
  - `name`: 라우트 이름
  - `network`: 네트워크
  - `dest_range`: 목적지 범위
  - `priority`: 우선순위
  - `next_hop_gateway`: 다음 홉 게이트웨이
  - `next_hop_instance`: 다음 홉 인스턴스
  - `next_hop_ip`: 다음 홉 IP
  - `tags`: 태그

- **VPCGateway**: VPN 게이트웨이 엔터티
  - `gateway_id`: 게이트웨이 식별자
  - `name`: 게이트웨이 이름
  - `description`: 설명
  - `network`: 네트워크
  - `region`: 리전
  - `vpn_interfaces`: VPN 인터페이스 목록

## 4. 비즈니스 로직 플로우 (Business Logic Flow)

### 4.1. 정상 플로우
1. **인증 검증**: Service Account 크리덴셜 유효성 확인
2. **VPC 네트워크 수집**: 프로젝트 내 모든 VPC 네트워크 목록 및 상세 정보 수집
3. **서브넷 정보 수집**: 각 리전별 서브넷 목록 및 구성 정보 수집
4. **방화벽 규칙 수집**: 프로젝트 레벨 방화벽 규칙 수집
5. **외부 IP 주소 수집**: 각 리전별 외부 IP 주소 목록 수집
6. **로드밸런서 수집**: 각 리전별 로드밸런서 및 포워딩 규칙 수집
7. **라우팅 테이블 수집**: 프로젝트 레벨 라우팅 규칙 수집
8. **VPN 게이트웨이 수집**: 각 리전별 VPN 게이트웨이 정보 수집
9. **데이터 변환**: SpaceONE 표준 모델로 변환
10. **응답 생성**: 각 리소스 타입별 Response 객체 생성

### 4.2. 예외 플로우
- **인증 실패**: 즉시 실패 반환, 재시도 없음
- **API 할당량 초과**: 지수 백오프로 재시도 (최대 3회)
- **네트워크 오류**: 연결 실패, 타임아웃에 대한 재시도 로직
- **개별 리소스 실패**: 로그 기록 후 다음 리소스 진행
- **데이터 파싱 실패**: 에러 응답 생성, 수집 계속

## 5. 외부 연동 (External Integration)

### 5.1. Google Cloud Compute Engine API (Networking)
- **의존 서비스**: Google Cloud Compute Engine API v1
- **엔드포인트**: `https://compute.googleapis.com`
- **인증 방식**: Service Account 키 파일 기반 OAuth 2.0
- **API 할당량**: 프로젝트당 분당 2000 요청
- **장애 대응**: 
  - HTTP 429 (할당량 초과): 지수 백오프 재시도
  - HTTP 404 (리소스 없음): 정상 처리 (빈 결과 반환)
  - 기타 HTTP 오류: 로그 기록 후 다음 리소스 진행

## 6. 보안 & 컴플라이언스 (Security & Compliance)

### 6.1. 인증 및 인가
- **Google Cloud 인증**: Service Account 키 파일 기반 OAuth 2.0
- **필수 IAM 권한**:
  - `compute.networks.list`
  - `compute.subnetworks.list`
  - `compute.firewalls.list`
  - `compute.addresses.list`
  - `compute.forwardingRules.list`
  - `compute.routes.list`
  - `compute.vpnGateways.list`
- **권한 범위**: 프로젝트 수준 읽기 전용 권한

## 7. 운영 & 모니터링 (Operations & Monitoring)

### 7.1. 성능 메트릭
- **수집 성능**: 프로젝트당 평균 25초 이내 수집 완료
- **처리량**: 동시 8개 프로젝트 병렬 처리 지원
- **오류율**: 5% 미만 유지 목표
- **메트릭 수집**: 
  - `network_count`: 프로젝트별 VPC 네트워크 개수
  - `subnet_count`: 총 서브넷 개수
  - `firewall_rule_count`: 총 방화벽 규칙 개수
  - `external_ip_count`: 총 외부 IP 주소 개수

## 8. 현재 구현 상태 (Implementation Status)

### 8.1. 구현 완료 기능
- ✅ **VPCNetworkManager**: VPC 네트워크 수집 및 상세 정보
- ✅ **VPCSubnetManager**: 서브넷 정보 수집
- ✅ **FirewallManager**: 방화벽 규칙 수집
- ✅ **ExternalIPAddressManager**: 외부 IP 주소 수집
- ✅ **LoadBalancingManager**: 로드밸런서 및 포워딩 규칙 수집
- ✅ **RouteManager**: 라우팅 테이블 수집
- ✅ **VPCGatewayManager**: VPN 게이트웨이 수집
- ✅ **메타데이터**: SpaceONE 콘솔 UI 레이아웃, 위젯

### 8.2. 주요 구현 특징
- **전체 네트워크 토폴로지 수집**: 프로젝트 내 모든 네트워킹 리소스 및 관계 정보 수집
- **보안 설정 정보**: 방화벽 규칙, 라우팅 정책 등 보안 관련 설정 포함
- **SpaceONE 모델 변환**: 수집된 모든 원시 데이터를 SpaceONE Cloud Service 모델 형식으로 변환
- **동적 UI 레이아웃**: 사용자가 수집된 리소스 정보를 쉽게 파악할 수 있는 UI 제공

### 8.3. 파일 구조
```
src/spaceone/inventory/
├── connector/networking/
│   ├── __init__.py
│   └── compute_v1.py               # Google Cloud Compute API 연동 (네트워킹)
├── manager/networking/
│   ├── __init__.py
│   ├── vpc_network_manager.py      # VPC 네트워크 비즈니스 로직
│   ├── vpc_subnet_manager.py       # 서브넷 비즈니스 로직
│   ├── firewall_manager.py         # 방화벽 비즈니스 로직
│   ├── external_ip_address_manager.py # 외부 IP 주소 비즈니스 로직
│   ├── load_balancing_manager.py   # 로드밸런서 비즈니스 로직
│   ├── route_manager.py            # 라우팅 비즈니스 로직
│   └── vpc_gateway_manager.py      # VPN 게이트웨이 비즈니스 로직
├── model/networking/
│   ├── vpc_network/                # VPC 네트워크 모델
│   ├── vpc_subnet/                 # 서브넷 모델
│   ├── firewall/                   # 방화벽 모델
│   ├── external_ip_address/        # 외부 IP 주소 모델
│   ├── load_balancing/             # 로드밸런서 모델
│   ├── route/                      # 라우팅 모델
│   └── vpc_gateway/                # VPN 게이트웨이 모델
└── service/
    └── collector_service.py        # 플러그인 엔트리포인트
```

### 8.4. 기술 스택
- **언어**: Python 3.8+
- **프레임워크**: SpaceONE Core 2.0+, SpaceONE Inventory, Schematics
- **Google Cloud SDK**: 
  - google-oauth2 (Service Account 인증)
  - googleapiclient (Discovery API 클라이언트)
- **테스트**: unittest, unittest.mock (Google Cloud API 모킹)
- **품질 관리**: ruff (린팅/포맷팅), pytest-cov (커버리지)

## 참고 자료

- [Google Cloud Compute Engine API 문서 (Networking)](https://cloud.google.com/compute/docs/reference/rest/v1)
- [SpaceONE 플러그인 개발 가이드](https://cloudforet.io/docs/)
- [현재 구현 소스 코드](../../../../src/spaceone/inventory/)
