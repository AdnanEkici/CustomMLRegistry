from __future__ import annotations

import os
import shutil
import sqlite3
import unittest
from typing import Final

from parameterized import parameterized

import tests.test_utils as test_utils
from app.logger.logger import ColorLogger as Logger
from app.model_registry.registry import ModelRegistry


class TestModelRegistry(unittest.TestCase):
    # Test paths.
    TEST_TMP_ROOT: Final = "tmp"
    TEST_TEMPORARY_DIRECTORY: Final = os.path.join(TEST_TMP_ROOT, "test_tmp_registry")
    TEST_LOGGER_PATH: Final = os.path.join("tests", "logs", "registry_test_logs", "test_registry.log")
    TEST_CASES_JSON_PATH: Final = os.path.join("tests", "integration_tests", "test_cases", "model_registry_test_cases.json")

    TEST_DATABASE_FILE_NAME: Final = os.path.join(TEST_TEMPORARY_DIRECTORY, "sqllite_model_registry_test.db")
    MODEL_TEST_BUCKET_NAME = "interview_test_bucket"

    # Test case keys.
    INSERT_TEST_CASE_KEY: Final = "test_insert_model_cases"
    DELETE_TEST_CASE_KEY: Final = "test_delete_model_cases"
    FETCH_TEST_CASE_KEY: Final = "test_fetch_model_cases"
    UPDATE_TEST_CASE_KEY: Final = "test_update_model_cases"

    registry_logger = Logger(log_file=TEST_LOGGER_PATH, debug_mode=True)
    registry = ModelRegistry(db_file=TEST_DATABASE_FILE_NAME, bucket_name=MODEL_TEST_BUCKET_NAME, logger=registry_logger)

    @classmethod
    def setUpClass(cls):
        if os.path.exists(cls.TEST_TEMPORARY_DIRECTORY):
            shutil.rmtree(cls.TEST_TEMPORARY_DIRECTORY)
        os.makedirs(cls.TEST_TEMPORARY_DIRECTORY, exist_ok=True)
        with open(cls.TEST_TEMPORARY_DIRECTORY + os.sep + "linear_regression_model.joblib", "w") as file:
            file.write("TESTING FILE")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.TEST_TMP_ROOT):
            shutil.rmtree(cls.TEST_TMP_ROOT)

    def test_create_tables(self):
        if os.path.exists(TestModelRegistry.TEST_DATABASE_FILE_NAME):
            shutil.rmtree(TestModelRegistry.TEST_DATABASE_FILE_NAME)
        TestModelRegistry.registry.create_tables()

        conn = sqlite3.connect(TestModelRegistry.TEST_DATABASE_FILE_NAME)
        cursor = conn.cursor()
        # Query the sqlite_master table to check for the existence of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        # List of expected tables
        expected_tables = {"model_metadata", "labels", "model_labels"}
        # Extract the table names from the result
        created_tables = {table[0] for table in tables}
        # Check if all expected tables are created
        self.assertTrue(expected_tables.issubset(created_tables), f"Expected tables {expected_tables} but found {created_tables}")
        # Close the database connection
        conn.close()

    def test_create_tables_if_exist(self, repeat_number: int = 20):
        for _ in range(repeat_number):
            TestModelRegistry.registry.create_tables()

        conn = sqlite3.connect(TestModelRegistry.TEST_DATABASE_FILE_NAME)
        cursor = conn.cursor()
        # Query the sqlite_master table to check for the existence of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        # List of expected tables
        expected_tables = {"model_metadata", "labels", "model_labels"}
        # Extract the table names from the result
        created_tables = {table[0] for table in tables}
        # Check if all expected tables are created
        self.assertTrue(expected_tables.issubset(created_tables), f"Expected tables {expected_tables} but found {created_tables}")
        # Close the database connection
        conn.close()

    @parameterized.expand(test_utils.load_test_cases(TEST_CASES_JSON_PATH, INSERT_TEST_CASE_KEY))
    def test_insert_model(
        self,
        test_name,
        expectation,
        model_name=None,
        model_version=None,
        features=None,
        model_file_path=None,
        model_description=None,
        framework=None,
        framework_version=None,
        training_data=None,
        hyperparameters=None,
        evaluation_metrics=None,
        model_author=None,
        status=None,
        labels=None,
    ):
        """Test the insertion of a pretrained model into the registry."""
        TestModelRegistry.registry.create_tables()  # Ensure tables are created

        if labels is None:
            labels = ["No Label"]

        is_inserted, _ = TestModelRegistry.registry.insert_model(
            name=model_name,
            features=features,
            version=model_version,
            file_path=model_file_path,
            description=model_description,
            framework=framework,
            framework_version=framework_version,
            training_data=training_data,
            hyperparameters=hyperparameters,
            evaluation_metrics=evaluation_metrics,
            model_author=model_author,
            status=status,
            labels=labels,
        )

        self.assertEqual(is_inserted, expectation, f"{test_name} expected insertion {expectation} but recieved {is_inserted}")

    @parameterized.expand(test_utils.load_test_cases(TEST_CASES_JSON_PATH, FETCH_TEST_CASE_KEY))
    def test_fetch_model(
        self,
        test_name,
        expectation,
        model_name=None,
        features=None,
        model_version=None,
        model_file_path=None,
        model_description=None,
        framework=None,
        framework_version=None,
        training_data=None,
        hyperparameters=None,
        evaluation_metrics=None,
        model_author=None,
        status=None,
        labels=None,
    ):
        expectation and self.__set_up_test_database(
            registry=TestModelRegistry.registry,
            model_name=model_name,
            features=features,
            model_version=model_version,
            model_file_path=model_file_path,
            model_description=model_description,
            framework=framework,
            framework_version=framework_version,
            training_data=training_data,
            hyperparameters=hyperparameters,
            evaluation_metrics=evaluation_metrics,
            model_author=model_author,
            status=status,
            labels=labels,
        )

        model_info_from_database, _ = TestModelRegistry.registry.fetch_model(name=model_name, version=model_version)

        if expectation:
            expected_model_data = {
                "name": model_name,
                "version": model_version,
                "file_path": model_file_path,
                "description": model_description,
                "framework": framework,
                "framework_version": framework_version,
                "training_data": training_data,
                "hyperparameters": hyperparameters,
                "evaluation_metrics": evaluation_metrics,
                "model_author": model_author,
                "status": status,
                "labels": labels,
            }

            # Check if all values in fetched model match the expected values
            for key, value in expected_model_data.items():
                self.assertEqual(model_info_from_database[key], value, f"Mismatch found for '{key}': {model_info_from_database[key]} != {value}")
        else:
            self.assertIsNone(model_info_from_database, msg=f"Expected return is None for {test_name}. Check again")

    @parameterized.expand(test_utils.load_test_cases(TEST_CASES_JSON_PATH, DELETE_TEST_CASE_KEY))
    def test_delete_model(
        self,
        test_name,
        expectation,
        model_name=None,
        model_version=None,
        model_file_path=None,
        model_description=None,
        framework=None,
        framework_version=None,
        training_data=None,
        hyperparameters=None,
        evaluation_metrics=None,
        model_author=None,
        status=None,
        labels=None,
    ):
        TestModelRegistry.registry.create_tables()  # Ensure tables are created

        expectation and self.__set_up_test_database(
            registry=TestModelRegistry.registry,
            model_name=model_name,
            model_version=model_version,
            model_file_path=model_file_path,
            model_description=model_description,
            framework=framework,
            framework_version=framework_version,
            training_data=training_data,
            hyperparameters=hyperparameters,
            evaluation_metrics=evaluation_metrics,
            model_author=model_author,
            status=status,
            labels=labels,
        )

        is_deleted, _ = TestModelRegistry.registry.delete_model(name=model_name, version=model_version)

        self.assertEqual(is_deleted, expectation, msg=f"{test_name} expected value for deletion was {expectation} but received {is_deleted}")

        fetched_data, _ = TestModelRegistry.registry.fetch_model(name=model_name, version=model_version)

        expectation and self.assertIsNone(fetched_data, msg=f"{test_name} should have successfully delete entry. Fetched data must be None !")

    @parameterized.expand(test_utils.load_test_cases(TEST_CASES_JSON_PATH, UPDATE_TEST_CASE_KEY))
    def test_update_model(self, test_name, expectation, initial_data, update_data):
        # Insert the initial model data
        expectation and self.__set_up_test_database(
            registry=TestModelRegistry.registry,
            model_name=initial_data["name"],
            features=initial_data["features"],
            model_version=initial_data["version"],
            model_file_path=initial_data["file_path"],
            model_description=initial_data["description"],
            framework=initial_data["framework"],
            framework_version=initial_data["framework_version"],
            training_data=initial_data["training_data"],
            hyperparameters=initial_data["hyperparameters"],
            evaluation_metrics=initial_data["evaluation_metrics"],
            model_author=initial_data["model_author"],
            status=initial_data["status"],
            labels=initial_data["labels"],
        )

        # Perform the update operation
        is_updated, _ = TestModelRegistry.registry.update_model(
            name=initial_data["name"],
            version=initial_data["version"],
            description=update_data.get("description"),
            framework=update_data.get("framework"),
            framework_version=update_data.get("framework_version"),
            model_author=update_data.get("model_author"),
            status=update_data.get("status"),
            labels=update_data.get("labels"),
        )

        # Assert that the update operation's success matches the expectation
        self.assertEqual(is_updated, expectation, msg=f"{test_name} expected value for updating was {expectation} but received {is_updated}")

        # Fetch the model from the database and validate the updated values
        model_info_from_database, _ = TestModelRegistry.registry.fetch_model(name=initial_data["name"], version=initial_data["version"])

        if expectation:
            expected_model_data = initial_data.copy()
            expected_model_data.update({k: v for k, v in update_data.items() if v is not None})

            # Check if all values in fetched model match the expected values
            for key, value in expected_model_data.items():
                self.assertEqual(model_info_from_database[key], value, f"Mismatch found for '{key}': {model_info_from_database[key]} != {value}")
        else:
            self.assertIsNone(model_info_from_database, msg=f"Expected return is None for {test_name}. Check again")

    # Helper Function
    def __set_up_test_database(
        self,
        registry=None,
        model_name: str | None = None,
        model_version: str | None = None,
        model_file_path: str | None = None,
        model_description: str | None = None,
        framework: str | None = None,
        framework_version: str | None = None,
        training_data: str | None = None,
        hyperparameters: str | None = None,
        evaluation_metrics: str | None = None,
        model_author: str | None = None,
        status: str | None = None,
        features: str | None = None,
        labels: list | None = None,
    ):
        # Ensure tables are created
        TestModelRegistry.registry.create_tables()

        # Insert model into the registry
        return registry.insert_model(
            name=model_name,
            features=features,
            version=model_version,
            file_path=model_file_path,
            description=model_description,
            framework=framework,
            framework_version=framework_version,
            training_data=training_data,
            hyperparameters=hyperparameters,
            evaluation_metrics=evaluation_metrics,
            model_author=model_author,
            status=status,
            labels=labels,
        )
