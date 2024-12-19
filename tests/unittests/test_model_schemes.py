from __future__ import annotations

import os
import unittest
from typing import Final

from marshmallow import ValidationError
from parameterized import parameterized

import tests.test_utils as test_utils
from app.model_registry.model_schema import AddDeleteModelSchema
from app.model_registry.model_schema import BaseModelSchema
from app.model_registry.model_schema import ModelSchema
from app.model_registry.model_schema import UpdateModelSchema


class TestSchemas(unittest.TestCase):
    TEST_CASES_JSON_PATH: Final = os.path.join(
        "tests",
        "unittests",
        "test_cases",
        "model_schema_test_cases.json",
    )

    # Test case keys.
    BASE_SCHEMA_TEST_CASE_KEY: Final = "base_model_schema_tests"
    MODEL_SCHEMA_CASE_KEY: Final = "model_schema_tests"
    UPDATE_SCHEMA_CASE_KEY: Final = "update_model_schema_tests"
    DELETE_SCHEMA_CASE_KEY: Final = "add_delete_model_schema_tests"

    @parameterized.expand(test_utils.load_test_cases(TEST_CASES_JSON_PATH, BASE_SCHEMA_TEST_CASE_KEY))
    def test_base_model_schema(self, _, expectation, data):
        if expectation:
            result = BaseModelSchema().load(data)
            self.assertEqual(result["name"], data.get("name"), msg="Name should not be changed")
            self.assertEqual(result["version"], data.get("version"), msg="Version should not be changed")
        else:
            with self.assertRaises(ValidationError, msg="Either name or validation is not given schema must raise ValidationError"):
                BaseModelSchema().load(data)

    @parameterized.expand(test_utils.load_test_cases(TEST_CASES_JSON_PATH, MODEL_SCHEMA_CASE_KEY))
    def test_model_schema(self, _, expectation, data):
        if expectation:
            result = ModelSchema().load(data)

            # Dynamically get all fields and their default values from ModelSchema
            schema_fields = ModelSchema._declared_fields
            for field_name, field_obj in schema_fields.items():
                expected_value = data.get(field_name, field_obj.missing if field_obj.missing is not None else None)
                self.assertEqual(result.get(field_name), expected_value, f"Field '{field_name}' does not match the expected value.")
        else:
            with self.assertRaises(ValidationError):
                ModelSchema().load(data)

    @parameterized.expand(test_utils.load_test_cases(TEST_CASES_JSON_PATH, DELETE_SCHEMA_CASE_KEY))
    def test_add_delete_model_schema(self, _, expectation, data):
        if expectation:
            result = AddDeleteModelSchema().load(data)
            schema_fields = AddDeleteModelSchema._declared_fields
            for field_name, field_obj in schema_fields.items():
                expected_value = data.get(field_name, field_obj.missing if field_obj.missing is not None else None)
                self.assertEqual(result.get(field_name), expected_value, f"Field '{field_name}' does not match the expected value.")
        else:
            with self.assertRaises(ValidationError):
                AddDeleteModelSchema().load(data)

    @parameterized.expand(test_utils.load_test_cases(TEST_CASES_JSON_PATH, UPDATE_SCHEMA_CASE_KEY))
    def test_update_model_schema(self, _, expectation, data):
        if expectation:
            result = UpdateModelSchema().load(data)
            schema_fields = UpdateModelSchema._declared_fields
            for field_name, field_obj in schema_fields.items():
                expected_value = data.get(field_name, field_obj.missing if field_obj.missing is not None else None)
                self.assertEqual(result.get(field_name), expected_value, f"Field '{field_name}' does not match the expected value.")
        else:
            with self.assertRaises(ValidationError):
                UpdateModelSchema().load(data)
