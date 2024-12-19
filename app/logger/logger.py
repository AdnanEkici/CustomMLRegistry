from __future__ import annotations

import logging
import os
from datetime import datetime

import colorlog


class ColorLogger:
    # Define standard and custom log levels
    DEBUG = logging.DEBUG  # 0
    INFO = logging.INFO  # 10
    STORAGE = 25
    WARNING = logging.WARNING  # 20
    ERROR = logging.ERROR  # 30
    DATABASE = 35
    CRITICAL = logging.CRITICAL  # 40
    DATA_BASE_ERROR = 45
    REGISTRY_ERROR = 65
    REGISTRY = 80
    STORAGE_ERROR = 90
    ENDPOINT = 100

    # Adding custom levels to logging module
    logging.addLevelName(STORAGE, "STORAGE")
    logging.addLevelName(DATABASE, "DATABASE")
    logging.addLevelName(DATA_BASE_ERROR, "DATA_BASE_ERROR")
    logging.addLevelName(REGISTRY, "REGISTRY")
    logging.addLevelName(REGISTRY_ERROR, "REGISTRY_ERROR")
    logging.addLevelName(STORAGE_ERROR, "STORAGE_ERROR")
    logging.addLevelName(ENDPOINT, "ENDPOINT")

    def __init__(self, log_file: str = "_default.log", debug_mode: bool = False):
        log_root_dir = os.path.dirname(log_file)
        log_file = os.path.basename(log_file)
        os.makedirs(log_root_dir, exist_ok=True)

        today = datetime.today().strftime("%Y_%m_%d")
        self.debug_mode = debug_mode

        self.logger_name = log_root_dir + os.sep + today + "_" + log_file if os.path.isdir(log_root_dir) else today + "_" + log_file
        self.logger = logging.getLogger(log_file)
        self.logger.setLevel(logging.DEBUG) if self.debug_mode else self.logger.setLevel(logging.INFO)

        # Create a ColorFormatter
        self.color_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s %(levelname)-8s%(reset)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",  # Format for date and time
            log_colors={
                "DEBUG": "cyan",
                "ENDPOINT": "cyan",
                "INFO": "blue",
                "STORAGE": "light_green",
                "STORAGE_ERROR": "light_red",
                "WARNING": "yellow",
                "ERROR": "red",
                "DATA_BASE_ERROR": "light_red",
                "CRITICAL": "red,bg_white",
                "DATABASE": "purple",
                "REGISTRY": "light_green",
                "REGISTRY_ERROR": "light_red",
            },
        )

        # Create a StreamHandler for console output
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(logging.DEBUG)
        self.stream_handler.setFormatter(self.color_formatter)

        # Create a FileHandler for file output
        self.file_handler = logging.FileHandler(self.logger_name)
        self.file_handler.setLevel(logging.DEBUG)

        # Create a Formatter for the file handler
        self.file_formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",  # Format for date and time
        )
        self.file_handler.setFormatter(self.file_formatter)

        # Add the handlers to the utils
        self.logger.addHandler(self.stream_handler)
        self.logger.addHandler(self.file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)

    def storage(self, message: str):
        self.logger.log(ColorLogger.STORAGE, message)

    def database(self, message: str):
        self.logger.log(ColorLogger.DATABASE, message)

    def database_error(self, message: str):
        self.logger.log(ColorLogger.DATA_BASE_ERROR, message)

    def registry(self, message: str):
        self.logger.log(ColorLogger.REGISTRY, message)

    def registry_error(self, message: str):
        self.logger.log(ColorLogger.REGISTRY_ERROR, message)

    def storage_error(self, message: str):
        self.logger.log(ColorLogger.STORAGE_ERROR, message)

    def endpoint(self, message: str):
        self.logger.log(ColorLogger.ENDPOINT, message)


if __name__ == "__main__":
    logger = ColorLogger(debug_mode=True)
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    logger.storage("Storage message")
    logger.storage_error("Storage error")
    logger.database("Database message")
    logger.registry("Registry message")
    logger.database_error("Database error")
    logger.registry_error("Registry error")
    logger.endpoint("Endpoint message")
