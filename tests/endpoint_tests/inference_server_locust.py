from __future__ import annotations

import json
import os
import random
from typing import Final

from locust import between
from locust import HttpUser
from locust import task

# locust -f  .\tests\endpoint_tests\inference_server_locust.py --host=http://localhost:2000


class InferenceServerLocustUser(HttpUser):
    wait_time = between(1, 2.5)
    print("You can start locust tests from http://localhost:8089/")  # noqa

    @staticmethod
    def load_model_payloads(file_path, case_key):
        """
        Load model payloads from a JSON file.

        Args:
            file_path (str): The path to the JSON file containing model payloads.
            case_key (str): Dict key for related test.

        Returns:
            list: A list of model payloads.
        """
        try:
            with open(file_path) as file:
                data = json.load(file)
                if case_key not in data:
                    raise ValueError(f"Key {case_key} not found in JSON data.")
                model_payloads = data[case_key]
                if not isinstance(model_payloads, list):
                    raise ValueError(f"{case_key} should be a list of payloads.")
                return model_payloads
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}")
            exit()
        except FileNotFoundError as e:
            print(f"File not found: {file_path}: {e}")
            exit()
        except Exception as e:
            print(f"An error occurred while loading model payloads: {e}")
            exit()

    UPLOAD_MODEL_PAYLOAD_TEST_CASES_PATH: Final = os.path.join("tests", "endpoint_tests", "test_cases", "inference_service_endpoint_test_cases.json")

    INFERENCE_PAYLOAD_TEST_CASE_KEY: Final = "inference_test_payloads"

    fetch_model_payload_test_cases: Final = load_model_payloads(
        file_path=UPLOAD_MODEL_PAYLOAD_TEST_CASES_PATH, case_key=INFERENCE_PAYLOAD_TEST_CASE_KEY
    )

    @task
    def test_predic(self):
        payload = random.choice(InferenceServerLocustUser.fetch_model_payload_test_cases)
        self.client.post("/predict", json=payload)
