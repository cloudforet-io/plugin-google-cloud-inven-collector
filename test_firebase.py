#!/usr/bin/env python3
"""
Firebase 앱 목록 테스트 스크립트
"""

import json
import os

from spaceone.inventory.connector.firebase.project import FirebaseProjectConnector


def test_firebase_apps():
    """
    특정 프로젝트의 Firebase 앱 목록을 테스트합니다.
    """

    # 서비스 계정 키 파일 경로 (환경 변수에서 가져오거나 직접 지정)
    service_account_key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not service_account_key_path or not os.path.exists(service_account_key_path):
        print(
            "Error: GOOGLE_APPLICATION_CREDENTIALS 환경 변수가 설정되지 않았거나 파일이 존재하지 않습니다."
        )
        print("다음 명령어로 설정하세요:")
        print(
            "export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json"
        )
        return

    try:
        # 서비스 계정 키 파일 읽기
        with open(service_account_key_path, "r") as f:
            secret_data = json.load(f)

        # Firebase Project Connector 초기화
        firebase_conn = FirebaseProjectConnector(secret_data=secret_data)

        print("Firebase 프로젝트 정보를 가져오는 중...")

        # 특정 프로젝트의 Firebase 정보 가져오기
        firebase_project_info = firebase_conn.get_firebase_project_info()

        print(f"\n프로젝트 ID: {firebase_project_info.get('projectId', 'N/A')}")
        print(f"Display Name: {firebase_project_info.get('displayName', 'N/A')}")
        print(f"Project Number: {firebase_project_info.get('projectNumber', 'N/A')}")
        print(f"State: {firebase_project_info.get('state', 'N/A')}")
        print(
            f"Has Firebase Services: {firebase_project_info.get('hasFirebaseServices', False)}"
        )
        print(f"App Count: {firebase_project_info.get('appCount', 0)}")

        # 플랫폼별 통계 출력
        platform_stats = firebase_project_info.get("platformStats", {})
        if platform_stats:
            print("\nPlatform Statistics:")
            for platform, count in platform_stats.items():
                print(f"  {platform}: {count} apps")

        # Firebase 앱들 출력
        firebase_apps = firebase_project_info.get("firebaseApps", [])
        if firebase_apps:
            print(f"\n총 {len(firebase_apps)}개의 Firebase 앱을 찾았습니다:\n")

            for i, app in enumerate(firebase_apps, 1):
                print(f"{i}. App Name: {app.get('displayName', 'N/A')}")
                print(f"   Platform: {app.get('platform', 'N/A')}")
                print(f"   App ID: {app.get('appId', 'N/A')}")
                print(f"   Namespace: {app.get('namespace', 'N/A')}")
                print(f"   State: {app.get('state', 'N/A')}")
                print()

        # JSON 형태로도 출력
        print("JSON 형태:")
        print(json.dumps(firebase_project_info, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_firebase_apps()
