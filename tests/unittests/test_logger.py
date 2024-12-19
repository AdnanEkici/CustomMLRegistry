from __future__ import annotations

import logging
import os
import shutil
import unittest
from typing import Final
from unittest.mock import MagicMock
from unittest.mock import patch

from logger.logger import ColorLogger


class TestColorLogger(unittest.TestCase):
    TEST_TMP_ROOT: Final = "tmp"
    TEST_LOGGER_PATH: Final = os.path.join(TEST_TMP_ROOT, "test_logs", "test.log")

    @patch("os.makedirs")
    @patch("logging.FileHandler")
    @patch("logging.StreamHandler")
    def setUp(self, mock_stream_handler, mock_file_handler, mock_makedirs):
        self.mock_stream_handler = MagicMock()
        self.mock_file_handler = MagicMock()

        mock_stream_handler.return_value = self.mock_stream_handler
        mock_file_handler.return_value = self.mock_file_handler

        self.logger = ColorLogger(log_file=TestColorLogger.TEST_LOGGER_PATH, debug_mode=True)

    def tearDown(self) -> None:
        return super().tearDown()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.TEST_TMP_ROOT):
            shutil.rmtree(cls.TEST_TMP_ROOT)

    def test_logger_initialization(self):
        self.assertEqual(self.logger.logger.level, logging.DEBUG)
        self.assertEqual(self.logger.debug_mode, True)
        self.assertTrue(self.mock_file_handler.setFormatter.called)
        self.assertTrue(self.mock_stream_handler.setFormatter.called)

    def test_log_debug(self):
        with patch.object(self.logger.logger, "debug") as mock_debug:
            self.logger.debug("Debug message")
            mock_debug.assert_called_once_with("Debug message")

    def test_log_info(self):
        with patch.object(self.logger.logger, "info") as mock_info:
            self.logger.info("Info message")
            mock_info.assert_called_once_with("Info message")

    def test_log_warning(self):
        with patch.object(self.logger.logger, "warning") as mock_warning:
            self.logger.warning("Warning message")
            mock_warning.assert_called_once_with("Warning message")

    def test_log_error(self):
        with patch.object(self.logger.logger, "error") as mock_error:
            self.logger.error("Error message")
            mock_error.assert_called_once_with("Error message")

    def test_log_critical(self):
        with patch.object(self.logger.logger, "critical") as mock_critical:
            self.logger.critical("Critical message")
            mock_critical.assert_called_once_with("Critical message")

    def test_log_custom_storage(self):
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.storage("Storage message")
            mock_log.assert_called_once_with(ColorLogger.STORAGE, "Storage message")

    def test_log_custom_database(self):
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.database("Database message")
            mock_log.assert_called_once_with(ColorLogger.DATABASE, "Database message")

    def test_log_custom_database_error(self):
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.database_error("Database error")
            mock_log.assert_called_once_with(ColorLogger.DATA_BASE_ERROR, "Database error")

    def test_log_custom_registry(self):
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.registry("Registry message")
            mock_log.assert_called_once_with(ColorLogger.REGISTRY, "Registry message")

    def test_log_custom_registry_error(self):
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.registry_error("Registry error")
            mock_log.assert_called_once_with(ColorLogger.REGISTRY_ERROR, "Registry error")

    def test_log_custom_storage_error(self):
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.storage_error("Storage error")
            mock_log.assert_called_once_with(ColorLogger.STORAGE_ERROR, "Storage error")

    def test_log_custom_endpoint(self):
        with patch.object(self.logger.logger, "log") as mock_log:
            self.logger.endpoint("Endpoint message")
            mock_log.assert_called_once_with(ColorLogger.ENDPOINT, "Endpoint message")

    @patch("os.path.isdir", return_value=True)
    def test_logger_creates_directory(self, mock_isdir):
        mock_isdir.return_value = False
        with patch("os.makedirs") as mock_makedirs:
            ColorLogger(log_file="test.log", debug_mode=True)
            mock_makedirs.assert_called_once()
