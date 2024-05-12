import json
import os
import unittest

from spaceone.core.unittest.runner import RichTestRunner
from spaceone.tester import TestCase, print_json

GOOGLE_APPLICATION_CREDENTIALS_PATH = os.environ.get(
    "GOOGLE_APPLICATION_CREDENTIALS", None
)

if GOOGLE_APPLICATION_CREDENTIALS_PATH is None:
    print(
        """
        ##################################################
        # ERROR 
        #
        # Configure your GCP credential first for test
        # https://console.cloud.google.com/apis/credentials

        ##################################################
        example)

        export GOOGLE_APPLICATION_CREDENTIALS="<PATH>" 
    """
    )
    exit


def _get_credentials():
    with open(GOOGLE_APPLICATION_CREDENTIALS_PATH) as json_file:
        json_data = json.load(json_file)
        return json_data


class TestCollector(TestCase):
    def test_init(self):
        v_info = self.inventory.Collector.init({"options": {}})
        print_json(v_info)

    def test_verify(self):
        options = {}
        secret_data = _get_credentials()
        v_info = self.inventory.Collector.verify(
            {"options": options, "secret_data": secret_data}
        )
        print_json(v_info)

    def test_collect(self):
        secret_data = _get_credentials()
        print(secret_data)
        """
        Options can be selected
        options = {"cloud_service_types": ["SQLWorkspace"]}
                        "service_code_mappers": {
                    "Compute Engine": "Test Gikang",
                    "Networking": "HaHa HoHo",
                    "Cloud SQL": "SQLSQL"
            }
        """
        options = {
            # "cloud_service_types": ["CloudFunctions"],
            "cloud_service_types": ["PubSub"],
            # "custom_asset_url": 'http://xxxxx.spaceone.dev/icon/google'
        }
        filter = {}

        resource_stream = self.inventory.Collector.collect(
            {"options": options, "secret_data": secret_data, "filter": filter}
        )

        print(resource_stream)
        for res in resource_stream:
            print_json(res)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
