#!/usr/bin/env python3
"""
Batch API 테스트 스크립트
"""

import os

from google.oauth2 import service_account
from googleapiclient import discovery


def test_batch_locations_api():
    """Batch API의 locations.list 엔드포인트를 테스트합니다."""

    # 서비스 계정 키 파일 경로 (환경 변수에서 가져오거나 직접 지정)
    credentials_file = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "path/to/your/service-account-key.json"
    )
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")

    try:
        # 서비스 계정 인증
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        # Batch API 클라이언트 생성
        batch_service = discovery.build("batch", "v1", credentials=credentials)

        # 프로젝트 기준으로 locations 조회
        name = f"projects/{project_id}"

        print(f"프로젝트 {project_id}의 Batch locations를 조회합니다...")

        # locations.list API 호출
        request = batch_service.projects().locations().list(name=name)
        response = request.execute()

        locations = response.get("locations", [])

        print(f"총 {len(locations)}개의 location을 찾았습니다:")
        print("-" * 50)

        for location in locations:
            print(f"Location ID: {location.get('locationId', 'N/A')}")
            print(f"Display Name: {location.get('displayName', 'N/A')}")
            print(f"Name: {location.get('name', 'N/A')}")
            print(f"Metadata: {location.get('metadata', {})}")
            print("-" * 30)

        return locations

    except Exception as e:
        print(f"오류 발생: {e}")
        return None


def test_batch_jobs_api():
    """Batch API의 jobs.list 엔드포인트를 테스트합니다."""

    # 서비스 계정 키 파일 경로 (환경 변수에서 가져오거나 직접 지정)
    credentials_file = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "path/to/your/service-account-key.json"
    )
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")

    try:
        # 서비스 계정 인증
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        # Batch API 클라이언트 생성
        batch_service = discovery.build("batch", "v1", credentials=credentials)

        # 먼저 locations 조회
        name = f"projects/{project_id}"
        locations_request = batch_service.projects().locations().list(name=name)
        locations_response = locations_request.execute()
        locations = locations_response.get("locations", [])

        print(f"프로젝트 {project_id}의 Batch jobs를 조회합니다...")

        total_jobs = 0

        for location in locations:
            location_id = location.get("locationId")
            if not location_id:
                continue

            print(f"\nLocation {location_id}에서 jobs 조회 중...")

            # 각 location에서 jobs 조회
            parent = f"projects/{project_id}/locations/{location_id}"
            jobs_request = (
                batch_service.projects().locations().jobs().list(parent=parent)
            )
            jobs_response = jobs_request.execute()

            jobs = jobs_response.get("jobs", [])
            total_jobs += len(jobs)

            print(f"  Location {location_id}: {len(jobs)}개의 job 발견")

            for job in jobs:
                print(f"    - Job ID: {job.get('uid', 'N/A')}")
                print(f"      Name: {job.get('displayName', 'N/A')}")
                print(f"      State: {job.get('state', 'N/A')}")
                print(f"      Create Time: {job.get('createTime', 'N/A')}")

        print(f"\n총 {total_jobs}개의 job을 찾았습니다.")
        return total_jobs

    except Exception as e:
        print(f"오류 발생: {e}")
        return None


if __name__ == "__main__":
    print("GCP Batch API 테스트 시작")
    print("=" * 50)

    # 환경 변수 확인
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        print("경고: GOOGLE_APPLICATION_CREDENTIALS 환경 변수가 설정되지 않았습니다.")
        print("서비스 계정 키 파일 경로를 직접 지정하거나 환경 변수를 설정하세요.")

    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        print("경고: GOOGLE_CLOUD_PROJECT 환경 변수가 설정되지 않았습니다.")
        print("프로젝트 ID를 직접 지정하거나 환경 변수를 설정하세요.")

    # Locations API 테스트 실행
    print("\n1. Batch Locations API 테스트")
    print("-" * 30)
    locations = test_batch_locations_api()

    if locations:
        print(
            f"\nLocations 테스트 완료: {len(locations)}개의 location을 성공적으로 조회했습니다."
        )
    else:
        print("\nLocations 테스트 실패: location 조회에 실패했습니다.")

    # Jobs API 테스트 실행
    print("\n2. Batch Jobs API 테스트")
    print("-" * 30)
    total_jobs = test_batch_jobs_api()

    if total_jobs is not None:
        print(f"\nJobs 테스트 완료: {total_jobs}개의 job을 성공적으로 조회했습니다.")
    else:
        print("\nJobs 테스트 실패: job 조회에 실패했습니다.")

    print("\n모든 테스트 완료!")
