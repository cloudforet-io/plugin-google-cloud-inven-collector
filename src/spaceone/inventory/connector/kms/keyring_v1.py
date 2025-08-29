import logging

from spaceone.inventory.libs.connector import GoogleCloudConnector

__all__ = ["KMSKeyRingV1Connector"]
_LOGGER = logging.getLogger(__name__)


class KMSKeyRingV1Connector(GoogleCloudConnector):
    """
    Google Cloud KMS KeyRing Connector

    KMS KeyRing 관련 API 호출을 담당하는 클래스
    - KeyRing 목록 조회
    - 효율적인 location 필터링 지원

    API 버전: v1
    참고: https://cloud.google.com/kms/docs/reference/rest/v1/projects.locations.keyRings/list
    """

    google_client_service = "cloudkms"
    version = "v1"

    # 일반적으로 사용되는 KMS location 목록 (성능 최적화를 위해)
    COMMON_KMS_LOCATIONS = [
        "global",
        "us-central1",
        "us-east1",
        "us-west1",
        "europe-west1",
        "asia-northeast1",
        "asia-northeast3",
        "asia-southeast1",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_locations(self):
        """
        KMS를 사용할 수 있는 모든 위치를 조회합니다.

        Returns:
            list: 모든 location 목록
        """
        try:
            request = (
                self.client.projects()
                .locations()
                .list(name=f"projects/{self.project_id}")
            )

            response = request.execute()
            _LOGGER.debug(f"Location list response: {response}")

            locations = response.get("locations", [])
            _LOGGER.info(f"Retrieved {len(locations)} locations")

            return locations

        except Exception as e:
            _LOGGER.error(f"Error listing locations: {e}")
            raise e

    def list_key_rings(self, location):
        """
        특정 위치의 모든 KeyRing을 조회합니다.

        API 응답 구조:
        {
          "keyRings": [
            {
              "name": "projects/{project_id}/locations/{location}/keyRings/{key_ring_id}",
              "createTime": "2024-01-01T12:34:56.789Z"
            }
          ],
          "nextPageToken": "...",
          "totalSize": 2
        }

        Args:
            location (str): 키링을 조회할 위치 (예: "global", "us-central1")

        Returns:
            list: 해당 location의 모든 keyring 목록
        """
        try:
            key_rings = []
            page_token = None

            while True:
                # API 요청 구성
                request_params = {
                    "parent": f"projects/{self.project_id}/locations/{location}",
                    "pageSize": 1000,  # 최대 페이지 크기 설정
                }

                if page_token:
                    request_params["pageToken"] = page_token

                # API 호출
                request = (
                    self.client.projects().locations().keyRings().list(**request_params)
                )

                response = request.execute()
                _LOGGER.debug(
                    f"KeyRing list response for location {location}: {response}"
                )

                # 응답에서 keyRings 목록 추출
                current_key_rings = response.get("keyRings", [])
                key_rings.extend(current_key_rings)

                # 다음 페이지 토큰 확인
                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            _LOGGER.info(
                f"Retrieved {len(key_rings)} key rings from location {location}"
            )
            return key_rings

        except Exception as e:
            _LOGGER.error(f"Error listing key rings in location {location}: {e}")
            raise e

    def list_all_key_rings(self, target_locations=None):
        """
        모든 위치 또는 지정된 위치의 KeyRing을 조회합니다.

        Args:
            target_locations (list, optional): 검색할 특정 location ID 목록.
                                             None이면 모든 location 검색

        Returns:
            list: 모든 위치의 keyring 목록 (location 정보 포함)
        """
        try:
            all_key_rings = []

            if target_locations:
                # 특정 위치들만 검색
                search_locations = target_locations
                _LOGGER.info(
                    f"Searching KeyRings in specified locations: {search_locations}"
                )
            else:
                # 모든 위치 검색
                location_data_list = self.list_locations()
                search_locations = [
                    loc.get("locationId", "")
                    for loc in location_data_list
                    if loc.get("locationId")
                ]
                _LOGGER.info(
                    f"Searching all {len(search_locations)} available locations"
                )

            # 각 location에서 KeyRing 검색
            found_locations = []
            for location_id in search_locations:
                if not location_id:
                    continue

                try:
                    # 각 위치별로 KeyRing 조회
                    key_rings = self.list_key_rings(location_id)

                    if key_rings:  # KeyRing이 있는 location만 처리
                        found_locations.append(location_id)

                        # Location 정보 조회 (KeyRing이 있을 때만)
                        location_data = self._get_location_info(location_id)

                        # 각 KeyRing에 location 정보 추가
                        for key_ring in key_rings:
                            key_ring["location_id"] = location_id
                            key_ring["location_data"] = location_data
                            all_key_rings.append(key_ring)

                except Exception as e:
                    _LOGGER.warning(
                        f"Failed to list key rings in location {location_id}: {e}"
                    )
                    continue

            _LOGGER.info(
                f"Retrieved {len(all_key_rings)} total key rings from {len(found_locations)} locations: {found_locations}"
            )
            return all_key_rings

        except Exception as e:
            _LOGGER.error(f"Error listing all key rings: {e}")
            raise e

    def _get_common_locations_only(self):
        """
        일반적인 location만 반환합니다 (대폭 축소된 검색).

        Returns:
            list: 일반적인 location ID 목록만
        """
        try:
            # 모든 사용 가능한 location 조회
            all_locations_data = self.list_locations()
            all_location_ids = [
                loc.get("locationId", "")
                for loc in all_locations_data
                if loc.get("locationId")
            ]

            # 일반적인 location 중에서 실제 존재하는 것만 반환
            common_locations = [
                loc for loc in self.COMMON_KMS_LOCATIONS if loc in all_location_ids
            ]

            _LOGGER.info(
                f"Using common locations only: {common_locations} (skipping {len(all_location_ids) - len(common_locations)} locations)"
            )
            return common_locations

        except Exception as e:
            _LOGGER.warning(
                f"Failed to get common locations, falling back to default: {e}"
            )
            return ["global", "us-central1", "asia-northeast3"]  # 최소한의 기본값

    def _get_optimized_location_list(self):
        """
        최적화된 location 검색 순서를 반환합니다.
        일반적인 location을 먼저 검색하고, 그 다음 나머지 location을 검색합니다.

        Returns:
            list: 최적화된 순서의 location ID 목록
        """
        try:
            # 모든 사용 가능한 location 조회
            all_locations_data = self.list_locations()
            all_location_ids = [
                loc.get("locationId", "")
                for loc in all_locations_data
                if loc.get("locationId")
            ]

            # 일반적인 location 먼저 (실제 존재하는 것만)
            priority_locations = [
                loc for loc in self.COMMON_KMS_LOCATIONS if loc in all_location_ids
            ]

            # 나머지 location들 (priority에 없는 것들)
            remaining_locations = [
                loc for loc in all_location_ids if loc not in self.COMMON_KMS_LOCATIONS
            ]

            # 우선순위 + 나머지 순서로 반환
            optimized_order = priority_locations + remaining_locations

            _LOGGER.debug(
                f"Optimized search order: Priority={priority_locations}, Remaining={len(remaining_locations)}"
            )
            return optimized_order

        except Exception as e:
            _LOGGER.warning(
                f"Failed to get optimized location list, falling back to all locations: {e}"
            )
            # 실패 시 모든 location 반환
            location_data_list = self.list_locations()
            return [
                loc.get("locationId", "")
                for loc in location_data_list
                if loc.get("locationId")
            ]

    def _get_location_info(self, location_id):
        """
        특정 location의 상세 정보를 조회합니다.

        Args:
            location_id (str): Location ID

        Returns:
            dict: Location 정보
        """
        try:
            # 간단한 location 정보 생성 (API 호출 최소화)
            return {
                "locationId": location_id,
                "displayName": self._get_location_display_name(location_id),
                "labels": {},
            }
        except Exception as e:
            _LOGGER.warning(f"Failed to get location info for {location_id}: {e}")
            return {"locationId": location_id, "displayName": location_id, "labels": {}}

    def _get_location_display_name(self, location_id):
        """
        Location ID를 사용자 친화적인 이름으로 변환합니다.

        Args:
            location_id (str): Location ID

        Returns:
            str: 표시할 이름
        """
        location_names = {
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

        return location_names.get(location_id, location_id)

    def list_crypto_keys(self, keyring_name):
        """
        특정 KeyRing의 모든 CryptoKey를 조회합니다.

        API 응답 구조:
        {
          "cryptoKeys": [
            {
              "name": "projects/{project_id}/locations/{location}/keyRings/{keyring}/cryptoKeys/{crypto_key}",
              "primary": {
                "name": "projects/{project_id}/locations/{location}/keyRings/{keyring}/cryptoKeys/{crypto_key}/cryptoKeyVersions/1",
                "state": "ENABLED"
              },
              "purpose": "ENCRYPT_DECRYPT",
              "createTime": "2024-01-01T12:34:56.789Z",
              "nextRotationTime": "2025-01-01T12:34:56.789Z",
              "versionTemplate": {
                "protectionLevel": "SOFTWARE",
                "algorithm": "GOOGLE_SYMMETRIC_ENCRYPTION"
              }
            }
          ],
          "nextPageToken": "...",
          "totalSize": 1
        }

        Args:
            keyring_name (str): KeyRing의 전체 이름 (예: "projects/test/locations/global/keyRings/my-keyring")

        Returns:
            list: 해당 KeyRing의 모든 CryptoKey 목록
        """
        try:
            crypto_keys = []
            page_token = None

            while True:
                # API 요청 구성
                request_params = {
                    "parent": keyring_name,
                    "pageSize": 1000,  # 최대 페이지 크기 설정
                }

                if page_token:
                    request_params["pageToken"] = page_token

                # API 호출
                request = (
                    self.client.projects()
                    .locations()
                    .keyRings()
                    .cryptoKeys()
                    .list(**request_params)
                )

                response = request.execute()
                _LOGGER.debug(
                    f"CryptoKey list response for keyring {keyring_name}: {response}"
                )

                # 응답에서 cryptoKeys 목록 추출
                current_crypto_keys = response.get("cryptoKeys", [])
                crypto_keys.extend(current_crypto_keys)

                # 다음 페이지 토큰 확인
                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            _LOGGER.info(
                f"Retrieved {len(crypto_keys)} crypto keys from keyring {keyring_name}"
            )
            return crypto_keys

        except Exception as e:
            _LOGGER.warning(f"Error listing crypto keys in keyring {keyring_name}: {e}")
            # CryptoKey 조회 실패는 warning으로 처리 (KeyRing은 있지만 CryptoKey가 없을 수 있음)
            return []

    def list_crypto_key_versions(self, crypto_key_name):
        """
        특정 CryptoKey의 모든 CryptoKeyVersion을 조회합니다.

        API 응답 구조:
        {
          "cryptoKeyVersions": [
            {
              "name": "projects/{project_id}/locations/{location}/keyRings/{keyring}/cryptoKeys/{crypto_key}/cryptoKeyVersions/1",
              "state": "ENABLED",
              "protectionLevel": "SOFTWARE",
              "algorithm": "GOOGLE_SYMMETRIC_ENCRYPTION",
              "createTime": "2024-01-01T12:34:56.789Z",
              "generateTime": "2024-01-01T12:34:56.789Z",
              "destroyTime": null,
              "destroyEventTime": null,
              "importJob": "",
              "importTime": null,
              "importFailureReason": "",
              "externalProtectionLevelOptions": {},
              "reimportEligible": false
            }
          ],
          "nextPageToken": "...",
          "totalSize": 2
        }

        Args:
            crypto_key_name (str): CryptoKey의 전체 이름
                                 (예: "projects/test/locations/global/keyRings/my-keyring/cryptoKeys/my-key")

        Returns:
            list: 해당 CryptoKey의 모든 CryptoKeyVersion 목록
        """
        try:
            crypto_key_versions = []
            page_token = None

            while True:
                # API 요청 구성
                request_params = {
                    "parent": crypto_key_name,
                    "pageSize": 1000,  # 최대 페이지 크기 설정
                    "view": "FULL",  # 전체 정보 조회
                }

                if page_token:
                    request_params["pageToken"] = page_token

                # API 호출
                request = (
                    self.client.projects()
                    .locations()
                    .keyRings()
                    .cryptoKeys()
                    .cryptoKeyVersions()
                    .list(**request_params)
                )

                response = request.execute()
                _LOGGER.debug(
                    f"CryptoKeyVersions list response for crypto key {crypto_key_name}: {response}"
                )

                # 응답에서 cryptoKeyVersions 목록 추출
                current_versions = response.get("cryptoKeyVersions", [])
                crypto_key_versions.extend(current_versions)

                # 다음 페이지 토큰 확인
                page_token = response.get("nextPageToken")
                if not page_token:
                    break

            _LOGGER.info(
                f"Retrieved {len(crypto_key_versions)} crypto key versions from crypto key {crypto_key_name}"
            )
            return crypto_key_versions

        except Exception as e:
            _LOGGER.warning(
                f"Error listing crypto key versions in crypto key {crypto_key_name}: {e}"
            )
            # CryptoKeyVersion 조회 실패는 warning으로 처리 (CryptoKey는 있지만 Version이 없을 수 있음)
            return []
