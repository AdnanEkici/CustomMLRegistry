from __future__ import annotations

import json
import os
import unittest
from typing import Final

from parameterized import parameterized

import tests.test_utils as test_utils


class TestTestUtilities(unittest.TestCase):
    TEST_JSON_PATH: Final = os.path.join("tests", "unittests", "test_cases", "utilities_test_cases.json")

    @classmethod
    def setUpClass(cls):
        sample_data = {
            "example_tests": [
                {"test_name": "test_case_1", "expectation": True, "data": {"name": "MyModel", "version": "1.0"}},
                {"test_name": "test_case_2", "expectation": False, "data": {"version": "1.0"}},
                {
                    "test_name": "test_case_3",
                    "expectation": True,
                    "data": {
                        "name": "ComplexModel",
                        "version": "2.0",
                        "details": {"author": "John Doe", "framework": "TensorFlow", "parameters": {"learning_rate": 0.01, "epochs": 100}},
                    },
                },
                {"test_name": "test_case_4", "expectation": True, "data": {"name": "EdgeCaseModel", "version": "3.0", "optional": None}},
                {"test_name": "test_case_5", "expectation": False, "data": {"name": "", "version": "1.0"}},
                {
                    "test_name": "test_case_6",
                    "expectation": True,
                    "data": {"name": "ModelWithList", "version": "4.0", "tags": ["AI", "ML", "DeepLearning"]},
                },
            ]
        }
        # Write the sample JSON data to a file
        with open(cls.TEST_JSON_PATH, "w") as f:
            json.dump(sample_data, f, indent=4)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.TEST_JSON_PATH):
            os.remove(cls.TEST_JSON_PATH)

    @parameterized.expand(
        [
            (
                "example_tests",
                [
                    ("test_case_1", True, {"name": "MyModel", "version": "1.0"}),
                    ("test_case_2", False, {"version": "1.0"}),
                    (
                        "test_case_3",
                        True,
                        {
                            "name": "ComplexModel",
                            "version": "2.0",
                            "details": {"author": "John Doe", "framework": "TensorFlow", "parameters": {"learning_rate": 0.01, "epochs": 100}},
                        },
                    ),
                    ("test_case_4", True, {"name": "EdgeCaseModel", "version": "3.0", "optional": None}),
                    ("test_case_5", False, {"name": "", "version": "1.0"}),  # Invalid empty name
                    ("test_case_6", True, {"name": "ModelWithList", "version": "4.0", "tags": ["AI", "ML", "DeepLearning"]}),
                ],
            ),
        ]
    )
    def test_load_test_cases(self, key, expected):
        result = test_utils.load_test_cases(self.TEST_JSON_PATH, key)
        self.assertEqual(result, expected, f"Test cases loaded for '{key}' do not match the expected output.")
