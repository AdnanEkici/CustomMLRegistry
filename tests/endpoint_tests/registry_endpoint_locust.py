from __future__ import annotations

import json
import os
import random
from typing import Final

from locust import between
from locust import HttpUser
from locust import task


class ModelRegistryLocustUser(HttpUser):
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

    UPLOAD_MODEL_PAYLOAD_TEST_CASES_PATH: Final = os.path.join("tests", "endpoint_tests", "test_cases", "model_registry_endpoint_test_cases.json")

    UPLOAD_MODEL_PAYLOAD_TEST_CASE_KEY: Final = "upload_model_payloads"
    FETCH_MODEL_PAYLOAD_TEST_CASE_KEY: Final = "fetch_model_test_cases"
    UPDATE_MODEL_PAYLOAD_TEST_CASE_KEY: Final = "update_model_test_cases"
    DELETE_MODEL_PAYLOAD_TEST_CASE_KEY: Final = "delete_model_test_cases"

    upload_model_payload_test_cases: Final = load_model_payloads(
        file_path=UPLOAD_MODEL_PAYLOAD_TEST_CASES_PATH, case_key=UPLOAD_MODEL_PAYLOAD_TEST_CASE_KEY
    )
    fetch_model_payload_test_cases: Final = load_model_payloads(
        file_path=UPLOAD_MODEL_PAYLOAD_TEST_CASES_PATH, case_key=UPLOAD_MODEL_PAYLOAD_TEST_CASE_KEY
    )
    update_model_payload_test_cases: Final = load_model_payloads(
        file_path=UPLOAD_MODEL_PAYLOAD_TEST_CASES_PATH, case_key=UPDATE_MODEL_PAYLOAD_TEST_CASE_KEY
    )
    delete_model_payload_test_cases: Final = load_model_payloads(
        file_path=UPLOAD_MODEL_PAYLOAD_TEST_CASES_PATH, case_key=DELETE_MODEL_PAYLOAD_TEST_CASE_KEY
    )

    @task
    def test_upload_model_detailed(self):
        """
        Test the /upload_model endpoint with a more detailed payload.
        """
        payload = random.choice(ModelRegistryLocustUser.upload_model_payload_test_cases)
        self.client.post("/upload_model", json=payload)

    @task
    def test_fetch_model(self):
        payload = random.choice(ModelRegistryLocustUser.fetch_model_payload_test_cases)
        self.client.get("/fetch_model", json=payload)

    @task
    def test_fetch_and_download_model(self):
        payload = random.choice(ModelRegistryLocustUser.fetch_model_payload_test_cases)
        self.client.get("/fetch_and_download_model", json=payload)

    @task
    def test_update_model(self):
        payload = random.choice(ModelRegistryLocustUser.update_model_payload_test_cases)
        self.client.put("/update_model_entry", json=payload)

    @task
    def test_remove_model(self):
        payload = random.choice(ModelRegistryLocustUser.delete_model_payload_test_cases)
        self.client.delete("/remove_model", json=payload)
