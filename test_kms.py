#!/usr/bin/env python3
"""
KMS KeyRing 플러그인 테스트 스크립트

이 스크립트는 Google Cloud KMS KeyRing 플러그인의 기능을 테스트합니다.
실제 Google Cloud 프로젝트에 연결하여 KeyRing 정보를 수집하고 출력합니다.

사용법:
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
    python test_kms.py
"""

import logging
import os
from unittest.mock import Mock

# SpaceONE 관련 import 경로 설정
os.environ["SPACEONE_PACKAGE"] = "plugin"

try:
    from src.spaceone.inventory.connector.kms.keyring_v1 import KMSKeyRingV1Connector
    from src.spaceone.inventory.manager.kms.keyring_manager import KMSKeyRingManager
except ImportError as e:
    print(f"Import 오류: {e}")
    print("SpaceONE 관련 패키지가 설치되지 않았거나 경로를 찾을 수 없습니다.")
    exit(1)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


def test_kms_connector():
    """KMS Connector 직접 테스트"""
    print("\n=== KMS KeyRing Connector 테스트 ===")

    # 테스트용 인증 정보 (환경변수에서 가져오기)
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path:
        print("GOOGLE_APPLICATION_CREDENTIALS 환경변수가 설정되지 않았습니다.")
        return

    try:
        # Connector 초기화
        connector = KMSKeyRingV1Connector(
            secret_data={
                "type": "service_account",
                "project_id": "your-project-id",  # 실제 프로젝트 ID로 변경
            }
        )

        # Location 목록 조회
        print("1. Location 목록 조회:")
        locations = connector.list_locations()
        print(f"   찾은 Location 수: {len(locations)}")

        for location in locations[:3]:  # 처음 3개만 출력
            location_id = location.get("locationId", "N/A")
            display_name = location.get("displayName", "N/A")
            print(f"   - {location_id}: {display_name}")

        # 모든 KeyRing 조회
        print("\n2. 모든 KeyRing 조회:")
        key_rings = connector.list_all_key_rings()
        print(f"   찾은 KeyRing 수: {len(key_rings)}")

        for keyring in key_rings[:5]:  # 처음 5개만 출력
            name = keyring.get("name", "N/A")
            location_id = keyring.get("location_id", "N/A")
            create_time = keyring.get("createTime", "N/A")
            print(f"   - {name} (Location: {location_id}, Created: {create_time})")

    except Exception as e:
        print(f"Connector 테스트 실패: {e}")


def test_kms_manager():
    """KMS Manager 테스트"""
    print("\n=== KMS KeyRing Manager 테스트 ===")

    try:
        # Mock locator 생성
        mock_locator = Mock()

        # Manager 초기화
        manager = KMSKeyRingManager()
        manager.locator = mock_locator

        # 테스트 파라미터
        params = {
            "secret_data": {
                "type": "service_account",
                "project_id": "your-project-id",  # 실제 프로젝트 ID로 변경
            },
            "options": {},
        }

        # Mock connector 설정
        mock_connector = Mock(spec=KMSKeyRingV1Connector)
        mock_connector.list_all_key_rings.return_value = [
            {
                "name": "projects/test-project/locations/global/keyRings/test-keyring-1",
                "createTime": "2024-01-01T12:00:00Z",
                "location_id": "global",
                "location_data": {
                    "locationId": "global",
                    "displayName": "Global",
                    "labels": {},
                },
            },
            {
                "name": "projects/test-project/locations/us-central1/keyRings/test-keyring-2",
                "createTime": "2024-01-02T12:00:00Z",
                "location_id": "us-central1",
                "location_data": {
                    "locationId": "us-central1",
                    "displayName": "US Central 1",
                    "labels": {"env": "prod"},
                },
            },
        ]

        mock_locator.get_connector.return_value = mock_connector

        # 클라우드 서비스 수집 테스트
        print("클라우드 서비스 수집 중...")
        resource_responses, error_responses = manager.collect_cloud_service(params)

        print(f"성공한 리소스: {len(resource_responses)}")
        print(f"실패한 리소스: {len(error_responses)}")

        # 결과 출력
        for i, response in enumerate(resource_responses):
            resource = response.resource
            print(f"\n리소스 {i + 1}:")
            print(f"  - 이름: {resource.name}")
            print(f"  - 계정: {resource.account}")
            print(f"  - 지역: {resource.region_code}")
            print(f"  - KeyRing ID: {resource.data.keyring_id}")
            print(f"  - Location: {resource.data.location_display_name}")
            print(f"  - 생성 시간: {resource.data.create_time}")

        # 에러 출력
        for error in error_responses:
            print(f"에러: {error}")

    except Exception as e:
        print(f"Manager 테스트 실패: {e}")
        import traceback

        traceback.print_exc()


def main():
    """메인 테스트 함수"""
    print("Google Cloud KMS KeyRing 플러그인 테스트 시작")
    print("=" * 50)

    # 환경 변수 확인
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path:
        print(f"인증 파일: {credentials_path}")
    else:
        print("주의: GOOGLE_APPLICATION_CREDENTIALS가 설정되지 않음")

    # 테스트 실행
    test_kms_connector()
    test_kms_manager()

    print("\n" + "=" * 50)
    print("테스트 완료")


if __name__ == "__main__":
    main()
