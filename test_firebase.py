#!/usr/bin/env python3
"""
Firebase 프로젝트 목록 테스트 스크립트
"""

import json
import os

from spaceone.inventory.connector.firebase.project import FirebaseProjectConnector


def test_firebase_projects():
    """
    Firebase 프로젝트 목록을 테스트합니다.
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

        print("Firebase 프로젝트 목록을 가져오는 중...")

        # 사용 가능한 Firebase 프로젝트 목록 가져오기
        available_projects = firebase_conn.list_available_projects()

        print(f"\n총 {len(available_projects)}개의 Firebase 프로젝트를 찾았습니다:\n")

        for i, project in enumerate(available_projects, 1):
            print(f"{i}. 프로젝트 ID: {project.get('projectId', 'N/A')}")
            print(f"   Display Name: {project.get('displayName', 'N/A')}")
            print(f"   Project Number: {project.get('projectNumber', 'N/A')}")
            print(f"   State: {project.get('state', 'N/A')}")

            # Resources 정보 출력
            resources = project.get("resources", {})
            if resources:
                print("   Resources:")
                for key, value in resources.items():
                    print(f"     {key}: {value}")

            print()

        # JSON 형태로도 출력
        print("JSON 형태:")
        print(json.dumps(available_projects, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_firebase_projects()
