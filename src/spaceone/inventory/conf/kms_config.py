# -*- coding: utf-8 -*-
"""
KMS 모듈 설정

이 파일은 KMS 관련 설정을 중앙 관리합니다.
"""

# KMS 일반적인 위치 목록 (성능 최적화를 위해 우선 검색)
COMMON_KMS_LOCATIONS = [
    "global",
    "us-central1",
    "us-east1", 
    "us-west1",
    "us-west2",
    "us-east4",
    "europe-west1",
    "europe-west2", 
    "europe-west3",
    "europe-west4",
    "asia-northeast1",
    "asia-northeast2",
    "asia-northeast3",
    "asia-southeast1",
    "asia-southeast2",
    "asia-south1",
    "asia-east1",
    "asia-east2",
    "australia-southeast1",
    "southamerica-east1",
    "northamerica-northeast1",
]

# Location 표시 이름 매핑
LOCATION_DISPLAY_NAMES = {
    "global": "Global",
    "us-central1": "Iowa (us-central1)",
    "us-east1": "South Carolina (us-east1)",
    "us-west1": "Oregon (us-west1)",
    "us-west2": "Los Angeles (us-west2)",
    "us-west3": "Salt Lake City (us-west3)",
    "us-west4": "Las Vegas (us-west4)",
    "us-east4": "Northern Virginia (us-east4)",
    "europe-west1": "Belgium (europe-west1)",
    "europe-west2": "London (europe-west2)",
    "europe-west3": "Frankfurt (europe-west3)",
    "europe-west4": "Netherlands (europe-west4)",
    "europe-west6": "Zurich (europe-west6)",
    "europe-north1": "Finland (europe-north1)",
    "asia-northeast1": "Tokyo (asia-northeast1)",
    "asia-northeast2": "Osaka (asia-northeast2)",
    "asia-northeast3": "Seoul (asia-northeast3)",
    "asia-southeast1": "Singapore (asia-southeast1)",
    "asia-southeast2": "Jakarta (asia-southeast2)",
    "asia-south1": "Mumbai (asia-south1)",
    "asia-east1": "Taiwan (asia-east1)",
    "asia-east2": "Hong Kong (asia-east2)",
    "australia-southeast1": "Sydney (australia-southeast1)",
    "australia-southeast2": "Melbourne (australia-southeast2)",
    "southamerica-east1": "São Paulo (southamerica-east1)",
    "northamerica-northeast1": "Montréal (northamerica-northeast1)",
}

# KMS API 관련 설정
KMS_API_CONFIG = {
    "page_size": 1000,  # 최대 페이지 크기 (실제 사용)
    "timeout": 30,      # API 타임아웃 (초) - 향후 활용 예정
    "retry_count": 3,   # 재시도 횟수 - 향후 활용 예정
}

# 로그 레벨 설정
LOG_LEVEL_CONFIG = {
    "keyring_not_found": "INFO",        # KeyRing이 없는 경우
    "crypto_key_not_found": "INFO",     # CryptoKey가 없는 경우  
    "location_access_error": "WARNING", # Location 접근 오류
    "api_error": "ERROR",               # 심각한 API 오류
}
