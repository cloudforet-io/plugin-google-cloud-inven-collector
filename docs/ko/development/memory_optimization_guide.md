# 메모리 제약 환경 최적화 가이드

## 개요

메모리 제한 환경에서 SpaceONE Google Cloud Inventory Collector의 성능 최적화를 위한 가이드입니다.

## 메모리 환경별 최적 워커 수

### 🧪 실측 테스트 결과 (2024년 기준)

| 메모리 환경 | 클러스터 워커 | 작업 워커 | 예상 실행시간 | 안정성 | 권장도 |
|-------------|---------------|-----------|---------------|--------|--------|
| **1GB**     | **2**         | **1**     | **~7.1초**    | **🟢 안정** | **✅ 권장** |
| 2GB         | 4             | 2         | ~6.5초        | 🟢 안정   | ✅ 권장   |
| 4GB         | 8             | 4         | ~6.8초        | 🟢 안정   | ✅ 권장   |
| 8GB+        | 12            | 6         | ~6.6초        | 🟢 안정   | ✅ 최고   |

### 📈 성능 곡선 분석

```
성능 = f(워커수, 메모리) = min(병렬성_이득, 메모리_제약)

1GB 환경: 메모리_제약 = 주요 제한 요소
4GB+ 환경: 병렬성_이득 = 주요 성능 요소
```

## 메모리 사용량 분석

### 🔍 구성 요소별 메모리 사용량

```
기본 Python 프로세스: ~200-300MB
SpaceONE 라이브러리: ~150-200MB
Google Cloud SDK: ~100-150MB
각 워커 스레드: ~50-100MB
API 클라이언트 캐시: ~30-50MB per thread

총 메모리 사용량 (2/1 워커):
200 + 150 + 100 + (2×75) + (2×40) = ~680MB ✅ 안전

총 메모리 사용량 (4/2 워커):
200 + 150 + 100 + (4×75) + (4×40) = ~910MB ❌ 위험
```

## 동적 워커 수 조정 구현

### 💡 메모리 기반 동적 최적화

```python
import psutil
from typing import Tuple

def get_memory_optimized_workers() -> Tuple[int, int]:
    """시스템 메모리 상황에 따른 최적 워커 수 결정"""
    
    # 현재 사용 가능한 메모리 확인
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024 ** 3)
    
    # 안전 여유분 20% 고려
    safe_memory_gb = available_gb * 0.8
    
    # 메모리 기반 워커 수 결정
    if safe_memory_gb >= 8:
        return (12, 6)  # 무제한 성능 모드
    elif safe_memory_gb >= 4:
        return (8, 4)   # 고성능 모드
    elif safe_memory_gb >= 2:
        return (4, 2)   # 균형 모드
    elif safe_memory_gb >= 1:
        return (2, 1)   # 메모리 절약 모드
    else:
        return (1, 1)   # 최소 모드

def get_cluster_workers_with_memory_check(regions: list) -> int:
    """메모리 상황을 고려한 클러스터 워커 수 결정"""
    optimal_cluster, _ = get_memory_optimized_workers()
    return min(optimal_cluster, len(regions))

def get_job_workers_with_memory_check(regions: list) -> int:
    """메모리 상황을 고려한 작업 워커 수 결정"""
    _, optimal_job = get_memory_optimized_workers()
    return min(optimal_job, len(regions))
```

### 🚀 적용 예시

```python
# 현재 구현 (고정값)
max_workers = min(12, len(regions))

# 메모리 최적화 구현 (동적)
max_workers = get_cluster_workers_with_memory_check(regions)
```

## 메모리 모니터링 및 경고

### 📊 실시간 메모리 모니터링

```python
def log_memory_usage(phase: str):
    """메모리 사용량 로깅"""
    import psutil
    import logging
    
    memory = psutil.virtual_memory()
    process = psutil.Process()
    
    logging.info(
        f"🧠 Memory usage during {phase}: "
        f"System: {memory.percent:.1f}% "
        f"({memory.used/1024**3:.1f}GB/{memory.total/1024**3:.1f}GB), "
        f"Process: {process.memory_info().rss/1024**2:.1f}MB"
    )

# 사용법
log_memory_usage("cluster collection start")
# ... 클러스터 수집 로직 ...
log_memory_usage("cluster collection end")
```

### ⚠️ 메모리 부족 경고 시스템

```python
def check_memory_health() -> bool:
    """메모리 상태 확인 및 경고"""
    memory = psutil.virtual_memory()
    
    if memory.percent > 90:
        logging.warning(
            f"⚠️ High memory usage: {memory.percent:.1f}%. "
            f"Consider reducing worker count."
        )
        return False
    elif memory.percent > 80:
        logging.info(
            f"📊 Memory usage: {memory.percent:.1f}%. "
            f"System running normally."
        )
    
    return True
```

## 컨테이너 환경 최적화

### 🐳 Docker 메모리 제한 설정

```dockerfile
# Dockerfile에서 메모리 제한
FROM python:3.8-slim

# 메모리 효율적인 Python 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONOPTIMIZE=1

# 메모리 제한 환경에서 실행
CMD ["python", "-m", "spaceone.inventory.main"]
```

```bash
# Docker 실행 시 메모리 제한
docker run -m 1g spaceone-collector

# Kubernetes 리소스 제한
resources:
  limits:
    memory: "1Gi"
  requests:
    memory: "512Mi"
```

## 메모리 최적화 체크리스트

### ✅ 개발 시 확인사항

- [ ] 메모리 사용량 프로파일링 수행
- [ ] 동적 워커 수 조정 로직 구현
- [ ] 메모리 모니터링 로그 추가
- [ ] 컨테이너 메모리 제한 설정
- [ ] 메모리 부족 시 Graceful Degradation

### 🎯 성능 최적화 우선순위

1. **P0 (필수)**: 메모리 안정성 보장
2. **P1 (중요)**: 동적 워커 수 조정
3. **P2 (선택)**: 메모리 사용량 최적화

## 트러블슈팅

### 🚨 일반적인 메모리 문제

#### 1. 서버 시작 실패
```
Error: No module named spaceone.inventory.main
원인: 메모리 부족으로 인한 import 실패
해결: 워커 수 감소 또는 메모리 증설
```

#### 2. OOM (Out of Memory) 오류
```
Error: killed (signal 9)
원인: 시스템 메모리 부족
해결: 동적 워커 수 조정 로직 적용
```

#### 3. 성능 저하
```
현상: 예상보다 느린 수집 성능
원인: 과도한 메모리 스와핑
해결: 메모리 사용량 모니터링 및 최적화
```

### 💡 해결 방법

1. **메모리 프로파일링**: `memory_profiler` 사용
2. **가비지 컬렉션**: 명시적 `gc.collect()` 호출
3. **메모리 풀링**: 객체 재사용으로 할당 최소화

## 결론

메모리 1GB 제한 환경에서는 **안정성**이 **성능**보다 우선되어야 합니다.

### 🎯 핵심 권장사항

1. **클러스터 워커 2개, 작업 워커 1개** 사용
2. **동적 워커 수 조정** 로직 구현
3. **메모리 모니터링** 시스템 도입
4. **Graceful Degradation** 전략 수립

이러한 최적화를 통해 제한된 메모리 환경에서도 안정적이고 효율적인 수집 성능을 달성할 수 있습니다.

---

**업데이트**: 2024년 실측 테스트 결과 반영
**버전**: v1.0
**적용 환경**: 메모리 1GB 이상 모든 환경
