from __future__ import annotations

import os
import shutil
import sqlite3
import unittest
from typing import Final

from parameterized import parameterized

from app.logger.logger import ColorLogger as Logger
from app.model_registry.sqllite_db import SQLiteDB


class TestSqlliteDatabase(unittest.TestCase):
    TEST_TEMPORARY_DIRECTORY: Final = "test_tmp"
    TEST_LOGGER_PATH: Final = os.path.join("tests", "logs", "sqllite_test_logs", "test_sqllite.log")
    TEST_DATABASE_FILE_NAME: Final = os.path.join(TEST_TEMPORARY_DIRECTORY, "sqllite_model_test.db")
    TEST_DATABASE_IN_MEMORY_NAME: Final = ":memory:"

    sql_logger = Logger(log_file=TEST_LOGGER_PATH, debug_mode=True)
    test_parameters_enter_success = [
        ("test_database_with_in_memory_enter", TEST_DATABASE_IN_MEMORY_NAME),
        ("test_database_with_file_enter", TEST_DATABASE_FILE_NAME),
    ]

    def setUp(self) -> None:
        os.makedirs(TestSqlliteDatabase.TEST_TEMPORARY_DIRECTORY, exist_ok=True)

    def tearDown(self) -> None:
        if os.path.exists(TestSqlliteDatabase.TEST_TEMPORARY_DIRECTORY):
            shutil.rmtree(TestSqlliteDatabase.TEST_TEMPORARY_DIRECTORY)

    @parameterized.expand(test_parameters_enter_success)
    def test_sqllite_enter_success(self, _, database_location):
        with SQLiteDB(database_location, logger=TestSqlliteDatabase.sql_logger) as conn:
            self.assertIsNotNone(conn, msg="Database connection object cannot be none !")

            self.assertIsInstance(conn, sqlite3.Connection, msg=f"Database connection object must be instance of {sqlite3.Connection}")

            self.assertEqual(conn.row_factory, sqlite3.Row, msg="Database row factory must be set.")

    @parameterized.expand(test_parameters_enter_success)
    def test_sqlite_enter_exit_success(self, _, database_location):
        """Test __enter__ and __exit__ methods for successful connection and proper cleanup."""

        with SQLiteDB(database_location, logger=TestSqlliteDatabase.sql_logger) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")

        with self.assertRaises(sqlite3.ProgrammingError, msg="Database connection should be closed after with block."):
            conn.execute("SELECT 1")
