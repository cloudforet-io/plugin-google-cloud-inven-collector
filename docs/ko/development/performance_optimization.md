# 병렬 처리 성능 최적화 가이드

## 개요

이 문서는 SpaceONE Google Cloud Inventory Collector에서 병렬 처리 성능 최적화를 위한 일반적인 방법론과 가이드라인을 제공합니다. 각 도메인(서비스)별로 최적의 워커 수와 성능 특성이 다르므로, 체계적인 성능 테스트를 통해 도메인별 최적화를 수행해야 합니다.

## 성능 최적화 방법론

### 🎯 핵심 원칙
- **도메인별 최적화**: 각 Google Cloud 서비스별로 최적의 워커 수가 다름
- **실측 데이터 기반**: 이론적 추정이 아닌 실제 성능 테스트 결과 활용
- **성능 곡선 분석**: 워커 수 증가에 따른 성능 변화를 체계적으로 측정
- **오버헤드 임계점 인식**: 과도한 워커 수로 인한 부작용 고려

### 📊 일반적인 성능 패턴

#### 성능 곡선의 일반적 형태
```
성능 = f(워커수) = 병렬성_이득 - 오버헤드_비용

최적점 = 도메인별로 상이 (실측을 통해 결정)
```

#### 성능 향상 구간 (저워커 → 최적워커)
- **선형 개선**: 워커 수 증가에 따른 지속적 성능 향상
- **병렬성 이득**: I/O 대기 시간 단축, 리소스 활용도 증가
- **효율성**: 도메인별로 10-50% 성능 향상 가능

#### 성능 저하 구간 (최적워커 → 과도워커)
- **급격한 저하**: 임계점 초과 시 성능 저하 시작
- **오버헤드 요인**:
  - 컨텍스트 스위칭 비용 증가
  - 메모리 경합 및 캐시 미스
  - Google Cloud API 레이트 리미트
  - 네트워크 대역폭 포화
  - 스레드 풀 관리 오버헤드

### 📈 도메인별 성능 특성 예시

| 도메인 | 특성 | 권장 시작점 | 테스트 범위 | 주요 고려사항 |
|--------|------|-------------|-------------|---------------|
| Compute | CPU 집약적 | 4-8 워커 | 2-16 워커 | 인스턴스 수, 리전 분산 |
| Storage | I/O 집약적 | 8-12 워커 | 4-20 워커 | 버킷 수, 객체 크기 |
| Dataproc | 혼합형 | 6-12 워커 | 2-16 워커 | 클러스터 수, 작업 복잡도 |
| BigQuery | 쿼리 집약적 | 2-6 워커 | 1-10 워커 | 쿼리 복잡도, 데이터 크기 |
| Cloud SQL | DB 연결 제한 | 2-4 워커 | 1-8 워커 | 연결 풀 크기, 쿼리 시간 |

## 최적화 가이드라인

### 🎯 워커 수 선택 전략

#### 일반적인 설정 패턴
```python
# 도메인별 최적화된 워커 수 설정 예시
def get_optimal_workers(domain: str, resource_count: int) -> int:
    """도메인별 최적 워커 수 반환"""
    domain_configs = {
        'compute': {'base': 6, 'max': 16},
        'storage': {'base': 10, 'max': 20}, 
        'dataproc': {'base': 8, 'max': 12},
        'bigquery': {'base': 4, 'max': 8},
        'cloudsql': {'base': 2, 'max': 6},
    }
    
    config = domain_configs.get(domain, {'base': 4, 'max': 10})
    return min(config['max'], max(config['base'], resource_count // 2))
```

#### 워커 수 결정 가이드라인
- **시작점**: 도메인별 권장 시작점에서 테스트 시작
- **점진적 증가**: 2배씩 증가시키며 성능 측정 (2→4→8→16)
- **최적점 탐색**: 성능이 최고점에 도달하는 워커 수 확인
- **임계점 확인**: 성능 저하가 시작되는 지점 식별
- **동적 조정**: `min(optimal_workers, resource_count)`로 리소스 수에 따른 자동 조정

### ⚡ 성능 최적화 원칙

1. **실측 데이터 기반 결정**: 이론적 추정이 아닌 실제 성능 테스트 결과 활용
2. **성능 곡선 분석**: 워커 수 증가에 따른 성능 변화를 체계적으로 측정
3. **오버헤드 임계점 인식**: 과도한 워커 수로 인한 부작용 고려
4. **비용 대비 효과 최적화**: 리소스 사용량 대비 최고의 성능 향상 달성
5. **도메인별 특성 고려**: 각 Google Cloud 서비스의 고유 특성 반영

### 🔍 성능 테스트 방법론

#### 테스트 환경 구성
- **측정 도구**: `grpcurl` + `time` 명령어 또는 내장 성능 측정
- **반복 횟수**: 각 설정당 최소 3-5회 측정하여 평균값 사용
- **환경 일관성**: 동일한 프로젝트, 동일한 시간대, 동일한 네트워크 환경
- **부하 조건**: 실제 운영 환경과 유사한 데이터 규모로 테스트

#### 표준 테스트 절차
1. **기준점 설정**: 도메인별 최소 권장 워커 수로 기준 성능 측정
2. **점진적 증가**: 워커 수를 단계적으로 증가시키며 측정 (2배씩 증가 권장)
3. **성능 곡선 분석**: 각 단계별 성능 변화를 그래프로 시각화
4. **임계점 확인**: 성능 저하가 시작되는 지점 식별
5. **최적점 결정**: 최고 성능을 보이는 워커 수 선택
6. **안정성 검증**: 최적 워커 수에서 여러 번 테스트하여 일관성 확인

#### 성능 측정 메트릭
- **처리 시간**: 전체 수집 완료 시간
- **처리량**: 단위 시간당 처리된 리소스 수
- **오류율**: 실패한 요청의 비율
- **타임아웃율**: 타임아웃된 요청의 비율
- **리소스 사용량**: CPU, 메모리 사용률

## 구현 세부사항

### 🛠️ 범용 코드 구현 패턴

#### 도메인별 최적화된 병렬 처리
```python
def list_resources(self, domain: str, **query) -> List[Dict]:
    """
    도메인별 최적화된 병렬 리소스 수집
    - 도메인별 최적 워커 수 자동 결정
    - 동적 타임아웃 설정
    - 성능 모니터링 내장
    """
    regions = self._get_regions()
    resource_list = []
    
    # 도메인별 최적 워커 수 결정
    max_workers = self._get_optimal_workers(domain, len(regions))
    timeout_config = self._get_timeout_config(domain)
    
    logger.info(
        f"🚀 Starting parallel {domain} collection: "
        f"regions={len(regions)}, max_workers={max_workers}, "
        f"timeout={timeout_config['individual']}s"
    )
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 병렬 처리 로직 구현
        futures = []
        for region in regions:
            future = executor.submit(
                self._collect_region_resources, 
                region, 
                timeout=timeout_config['individual']
            )
            futures.append(future)
        
        # 결과 수집 및 타임아웃 처리
        for future in as_completed(futures, timeout=timeout_config['global']):
            try:
                result = future.result()
                resource_list.extend(result)
            except TimeoutError:
                logger.warning(f"Region collection timed out")
            except Exception as e:
                logger.error(f"Region collection failed: {e}")
    
    return resource_list

def _get_optimal_workers(self, domain: str, region_count: int) -> int:
    """도메인별 최적 워커 수 반환"""
    # 성능 테스트 결과 기반 설정
    domain_configs = {
        'compute': {'base': 6, 'max': 16, 'ratio': 0.5},
        'storage': {'base': 10, 'max': 20, 'ratio': 0.8}, 
        'dataproc': {'base': 8, 'max': 12, 'ratio': 0.6},
        'bigquery': {'base': 4, 'max': 8, 'ratio': 0.3},
        'cloudsql': {'base': 2, 'max': 6, 'ratio': 0.2},
    }
    
    config = domain_configs.get(domain, {'base': 4, 'max': 10, 'ratio': 0.4})
    calculated = int(region_count * config['ratio'])
    
    return min(config['max'], max(config['base'], calculated))

def _get_timeout_config(self, domain: str) -> Dict[str, int]:
    """도메인별 타임아웃 설정 반환"""
    timeout_configs = {
        'compute': {'individual': 45, 'global': 120},
        'storage': {'individual': 30, 'global': 90},
        'dataproc': {'individual': 60, 'global': 180},
        'bigquery': {'individual': 90, 'global': 300},
        'cloudsql': {'individual': 30, 'global': 90},
    }
    
    return timeout_configs.get(domain, {'individual': 45, 'global': 120})
```

### 📝 성능 모니터링 및 로깅

#### 표준 성능 로깅 패턴
```python
# 수집 시작 로깅
logger.info(
    f"🚀 Starting parallel {domain} collection: "
    f"regions={len(regions)}, max_workers={max_workers}, "
    f"individual_timeout={timeout_config['individual']}s, "
    f"global_timeout={timeout_config['global']}s"
)

# 성능 메트릭 로깅
start_time = time.time()
# ... 수집 로직 ...
end_time = time.time()

logger.info(
    f"✅ Completed {domain} collection: "
    f"duration={end_time - start_time:.2f}s, "
    f"resources_collected={len(resource_list)}, "
    f"throughput={len(resource_list)/(end_time - start_time):.2f} resources/sec"
)
```

#### 성능 메트릭 추적
- **수집 시간**: 도메인별 목표 시간 범위 설정
- **처리량**: 단위 시간당 처리된 리소스 수 측정
- **오류율**: 전체 요청 대비 실패 비율 (목표: 5% 미만)
- **타임아웃율**: 전체 요청 대비 타임아웃 비율 (목표: 2% 미만)
- **워커 효율성**: 워커당 평균 처리 시간

## 향후 최적화 방향

### 🔮 추가 최적화 기회

1. **적응형 워커 조정**: 실시간 성능 모니터링 기반 동적 워커 수 조정
2. **배치 크기 최적화**: 도메인별 API 호출 배치 크기 최적화
3. **지능형 캐싱**: 리전 목록, 메타데이터 캐싱을 통한 추가 성능 향상
4. **비동기 I/O**: asyncio 기반 비동기 처리 도입 검토
5. **부하 분산**: 리전별 부하에 따른 워커 분배 최적화

### 📊 지속적 모니터링 체계

1. **성능 회귀 방지**: 
   - 자동화된 성능 테스트 파이프라인 구축
   - 성능 기준선 대비 회귀 감지 알림
2. **환경 변화 대응**: 
   - Google Cloud API 변경사항 모니터링
   - 새로운 리전 추가 시 성능 영향 분석
3. **확장성 검증**: 
   - 대용량 환경에서의 성능 검증
   - 리소스 수 증가에 따른 성능 변화 추적
4. **리소스 최적화**: 
   - CPU, 메모리 사용량 프로파일링
   - 네트워크 대역폭 사용량 모니터링

### 🎯 도메인별 최적화 로드맵

| 우선순위 | 도메인 | 현재 상태 | 최적화 목표 | 예상 효과 |
|----------|--------|-----------|-------------|-----------|
| 1 | Compute | 기본 설정 | 워커 수 최적화 | 20-40% 향상 |
| 2 | Storage | 기본 설정 | 배치 처리 최적화 | 30-50% 향상 |
| 3 | Dataproc | ✅ 최적화 완료 | 미세 조정 | 5-10% 추가 향상 |
| 4 | BigQuery | 기본 설정 | 쿼리 최적화 | 15-25% 향상 |
| 5 | Cloud SQL | 기본 설정 | 연결 풀 최적화 | 10-20% 향상 |

## 결론

이 문서는 SpaceONE Google Cloud Inventory Collector의 범용적인 성능 최적화 방법론을 제시합니다.

**핵심 원칙**:
- ✅ **도메인별 특성 고려**: 각 서비스의 고유한 성능 특성 반영
- ✅ **실측 데이터 기반**: 이론이 아닌 실제 테스트 결과로 최적화
- ✅ **체계적 접근**: 표준화된 테스트 절차와 메트릭 활용
- ✅ **지속적 개선**: 모니터링과 피드백을 통한 지속적 최적화

**적용 방법**:
1. 도메인별 성능 특성 파악
2. 체계적인 성능 테스트 수행
3. 최적 워커 수 및 설정 결정
4. 지속적 모니터링 및 개선

이러한 방법론을 통해 각 도메인에서 10-50%의 성능 향상을 달성할 수 있으며, 전체 시스템의 효율성과 안정성을 크게 개선할 수 있습니다.

## 메모리 제약 환경 특화 최적화 (v2.1)

### 🧠 메모리 1GB 제약 환경 Dataproc 최적화 사례

#### 실측 테스트 결과
- **환경**: 메모리 1GB 제한
- **최적 설정**: 클러스터 2 워커, 작업 1 워커
- **성능**: 7.1초 (안정적)
- **메모리 임계점**: 4개 이상 워커에서 실행 불가

#### 메모리 기반 성능 특성
```python
# 메모리 제약 환경에서는 다른 최적화 전략 필요
if memory_gb <= 1:
    # 안정성 우선 모드
    MAX_WORKERS = 2
    MAX_JOB_WORKERS = 1
elif memory_gb <= 2:
    # 균형 모드
    MAX_WORKERS = 4
    MAX_JOB_WORKERS = 2
else:
    # 성능 우선 모드
    MAX_WORKERS = 12
    MAX_JOB_WORKERS = 6
```

#### 핵심 학습 사항
1. **메모리가 제한 요소**: 워커 수보다 메모리 안정성이 우선
2. **안전 범위 준수**: 임계점을 넘으면 전체 시스템 실패
3. **합리적 트레이드오프**: 성능 대신 안정성 선택의 정당성
4. **환경별 최적화**: 하나의 설정이 모든 환경에 적합하지 않음

---

**참고 자료**:
- [메모리 최적화 가이드](memory_optimization_guide.md)
- [프로젝트 규칙 - 병렬 처리 최적화](../../../.cursor/rules/project-rules.mdc#134-병렬-처리-워커-수-최적화-가이드라인)
- [각 도메인별 PRD 문서](../prd/)
- [CHANGELOG - Performance 섹션](../../../CHANGELOG.md)
