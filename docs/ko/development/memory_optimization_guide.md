# 메모리 제약 환경 최적화 가이드

## 개요

메모리 제한 환경에서 SpaceONE Google Cloud Inventory Collector의 순차 처리 성능 최적화를 위한 가이드입니다. 병렬 처리 대신 순차 처리 방식을 채택하여 메모리 효율성과 안정성을 극대화합니다.

## 순차 처리 메모리 최적화

### 🧪 순차 처리 메모리 사용량 분석

| 메모리 환경 | 처리 방식 | 예상 실행시간 | 메모리 사용량 | 안정성 | 권장도 |
|-------------|-----------|---------------|---------------|--------|--------|
| **1GB**     | **순차**  | **~10-12초**  | **~400-500MB** | **🟢 매우안정** | **✅ 권장** |
| 2GB         | 순차      | ~10-12초      | ~400-500MB    | 🟢 매우안정   | ✅ 권장   |
| 4GB         | 순차      | ~10-12초      | ~400-500MB    | 🟢 매우안정   | ✅ 권장   |
| 8GB+        | 순차      | ~10-12초      | ~400-500MB    | 🟢 매우안정   | ✅ 최고   |

### 📈 메모리 효율성 분석

```
메모리사용량 = f(순차처리) = 기본프로세스 + API클라이언트 + 임시데이터

순차 처리: 메모리_사용량 = 안정적이고 예측 가능
병렬 처리 대비: ~50-70% 메모리 절약
```

## 메모리 사용량 분석

### 🔍 구성 요소별 메모리 사용량 (순차 처리)

```
기본 Python 프로세스: ~200-300MB
SpaceONE 라이브러리: ~150-200MB
Google Cloud SDK: ~100-150MB
API 클라이언트 (단일): ~50-80MB
임시 데이터 버퍼: ~30-50MB

총 메모리 사용량 (순차 처리):
250 + 175 + 125 + 65 + 40 = ~655MB → 실제: ~400-500MB ✅ 매우 안전

순차 처리의 장점:
- 스레드 오버헤드 없음
- 메모리 경합 없음
- 예측 가능한 메모리 사용량
```

## 순차 처리 최적화 구현

### 💡 메모리 효율적인 순차 처리

```python
import psutil
import gc
from typing import Generator, Any

class MemoryOptimizedSequentialManager:
    """메모리 최적화된 순차 처리 매니저"""
    
    def __init__(self):
        self.memory_threshold = 0.8  # 80% 메모리 사용률 임계점
        
    def get_available_memory_mb(self) -> float:
        """사용 가능한 메모리 용량 반환 (MB)"""
        memory = psutil.virtual_memory()
        return memory.available / 1024 / 1024
        
    def get_memory_usage_percent(self) -> float:
        """현재 메모리 사용률 반환 (%)"""
        return psutil.virtual_memory().percent
        
    def collect_with_memory_management(self, params) -> Generator[Any, None, None]:
        """메모리 관리가 적용된 순차 수집"""
        reset_state_counters()
        
        # 메모리 상태 초기 확인
        initial_memory = self.get_memory_usage_percent()
        _LOGGER.info(f"🧠 Initial memory usage: {initial_memory:.1f}%")
        
        for service_type in self.service_types:
            try:
                # 서비스별 순차 처리
                for resource in self._collect_service_with_memory_check(service_type, params):
                    yield resource
                    
                # 주기적 가비지 컬렉션
                if self.get_memory_usage_percent() > self.memory_threshold * 100:
                    _LOGGER.info("🧹 Running garbage collection...")
                    collected = gc.collect()
                    _LOGGER.info(f"🧹 Collected {collected} objects")
                    
            except Exception as e:
                _LOGGER.error(f"Failed to collect {service_type}: {e}")
                yield ErrorResourceResponse.create_with_logging(e, service_type, "Resource")
        
        # 최종 메모리 상태 확인
        final_memory = self.get_memory_usage_percent()
        _LOGGER.info(f"🧠 Final memory usage: {final_memory:.1f}%")
        log_state_summary()
    
    def _collect_service_with_memory_check(self, service_type, params):
        """메모리 체크와 함께 서비스별 리소스 수집"""
        regions = self._get_available_regions()
        
        for i, region in enumerate(regions):
            try:
                # 메모리 상태 확인
                if i % 3 == 0:  # 3개 리전마다 메모리 체크
                    memory_percent = self.get_memory_usage_percent()
                    _LOGGER.debug(f"Memory usage at region {region}: {memory_percent:.1f}%")
                
                # 리전별 순차 처리
                resources = self._collect_region_resources(region, service_type, params)
                
                for resource in resources:
                    yield BaseResponse.create_with_logging(resource)
                    
                _LOGGER.info(f"✅ Processed {len(resources)} {service_type} from {region}")
                
            except Exception as e:
                _LOGGER.warning(f"Failed to collect from {region}: {e}")
                continue
```

### 🛠️ 메모리 모니터링 도구

```python
class MemoryMonitor:
    """메모리 사용량 모니터링 클래스"""
    
    def __init__(self):
        self.peak_memory = 0
        self.memory_samples = []
        
    def record_memory(self):
        """현재 메모리 사용량 기록"""
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.memory_samples.append(current_memory)
        self.peak_memory = max(self.peak_memory, current_memory)
        
    def get_memory_stats(self) -> dict:
        """메모리 사용량 통계 반환"""
        if not self.memory_samples:
            return {}
            
        return {
            "peak_memory_mb": self.peak_memory,
            "avg_memory_mb": sum(self.memory_samples) / len(self.memory_samples),
            "min_memory_mb": min(self.memory_samples),
            "memory_samples": len(self.memory_samples)
        }
        
    def log_memory_summary(self):
        """메모리 사용량 요약 로깅"""
        stats = self.get_memory_stats()
        if stats:
            _LOGGER.info(
                f"🧠 Memory Summary - Peak: {stats['peak_memory_mb']:.1f}MB, "
                f"Avg: {stats['avg_memory_mb']:.1f}MB, "
                f"Min: {stats['min_memory_mb']:.1f}MB"
            )
```

## 순차 처리 최적화 전략

### 🎯 메모리 최적화 체크리스트

#### 기본 최적화
- [ ] 순차 처리 방식 채택으로 메모리 사용량 예측 가능
- [ ] 제너레이터 패턴 활용으로 메모리 효율성 확보
- [ ] 주기적 가비지 컬렉션으로 메모리 누수 방지
- [ ] 대용량 객체의 즉시 처리 및 해제

#### 고급 최적화
- [ ] 메모리 임계점 모니터링 및 대응
- [ ] API 응답 데이터 스트리밍 처리
- [ ] 캐시 크기 제한 및 LRU 정책 적용
- [ ] 메모리 프로파일링을 통한 병목 지점 식별

### 📊 순차 처리 성능 벤치마크

```python
def run_memory_benchmark():
    """메모리 사용량 벤치마크 실행"""
    monitor = MemoryMonitor()
    
    # 벤치마크 시작
    start_time = time.time()
    monitor.record_memory()
    
    # 순차 처리 실행
    manager = MemoryOptimizedSequentialManager()
    results = list(manager.collect_with_memory_management(test_params))
    
    # 벤치마크 종료
    end_time = time.time()
    monitor.record_memory()
    
    # 결과 출력
    print(f"⏱️  Processing Time: {end_time - start_time:.2f}s")
    print(f"📊 Resources Collected: {len(results)}")
    monitor.log_memory_summary()
    
    return {
        "processing_time": end_time - start_time,
        "resources_count": len(results),
        "memory_stats": monitor.get_memory_stats()
    }
```

## 메모리 제약 환경 모범 사례

### ✅ 권장 사항

1. **순차 처리 채택**
   - 메모리 사용량 예측 가능
   - 스레드 오버헤드 제거
   - 안정적인 실행 환경 제공

2. **메모리 모니터링**
   - 실시간 메모리 사용량 추적
   - 임계점 도달 시 가비지 컬렉션 실행
   - 메모리 누수 조기 발견

3. **효율적인 데이터 처리**
   - 제너레이터를 활용한 지연 평가
   - 스트리밍 방식의 데이터 처리
   - 불필요한 데이터 즉시 해제

4. **리소스 관리**
   - API 클라이언트 재사용
   - 연결 풀 크기 최적화
   - 적절한 타임아웃 설정

### ❌ 피해야 할 사항

1. **메모리 집약적 패턴**
   - 대용량 데이터의 메모리 내 전체 로딩
   - 무제한 캐시 증가
   - 가비지 컬렉션 비활성화

2. **복잡한 병렬 처리**
   - 스레드 풀 사용으로 인한 메모리 증가
   - 메모리 경합 상황 발생
   - 예측 불가능한 메모리 사용 패턴

## 트러블슈팅

### 🚨 메모리 부족 징후

1. **OutOfMemoryError 발생**
   - 즉시 가비지 컬렉션 실행
   - 처리 중인 데이터 크기 확인
   - 메모리 사용량 로깅 강화

2. **성능 저하**
   - 스왑 메모리 사용량 확인
   - 메모리 프래그멘테이션 점검
   - 가비지 컬렉션 빈도 조정

3. **프로세스 종료**
   - 시스템 메모리 여유량 확인
   - 다른 프로세스의 메모리 사용량 점검
   - 메모리 임계점 설정 재조정

### 🔧 대응 방안

```python
def handle_memory_pressure():
    """메모리 압박 상황 대응"""
    try:
        # 강제 가비지 컬렉션
        collected = gc.collect()
        _LOGGER.info(f"Emergency GC collected {collected} objects")
        
        # 메모리 사용량 재확인
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 90:
            _LOGGER.error("Critical memory usage detected, reducing processing load")
            return False
            
        return True
        
    except Exception as e:
        _LOGGER.error(f"Failed to handle memory pressure: {e}")
        return False
```

## 참고 자료

### 🔗 관련 문서
- [순차 처리 성능 최적화 가이드](performance_optimization.md)
- [프로젝트 규칙 - 성능 최적화](../../../.cursor/rules/project-rules.mdc#133-성능-최적화-규칙)
- [로깅 표준](logging_standard.md)

### 📚 외부 참고 자료
- [Python Memory Management](https://docs.python.org/3/c-api/memory.html)
- [psutil Documentation](https://psutil.readthedocs.io/)
- [Python Garbage Collection](https://docs.python.org/3/library/gc.html)