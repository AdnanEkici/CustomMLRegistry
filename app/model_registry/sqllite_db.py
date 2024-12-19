from __future__ import annotations

import sqlite3
from sqlite3 import Error

from logger.logger import ColorLogger


class SQLiteDB:
    """
    Initialize the SQLiteDB with the database file path.

    Args:
        db_file (str): The path to the SQLite database file.
    """

    def __init__(self, db_file: str, logger: ColorLogger):
        self.db_file: str = db_file
        self.conn: None = None
        self.logger = logger

    def __enter__(self):
        """
        Enter the runtime context for the SQLiteDB object.

        This method is called when the `with` statement is executed. It establishes a connection
        to the SQLite database and sets the row factory to return rows as dictionary-like objects.

        Returns:
            sqlite3.Connection: The SQLite connection object.
        """
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row  # Set row factory to return dict-like rows
            self.logger.database(f"Connected to SQLite database '{self.db_file}'")
            return self.conn
        except Error as e:
            self.logger.database_error(f"Error connecting to SQLite database: {e}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the runtime context for the SQLiteDB object.

        This method is called when the `with` statement is exited. It closes the SQLite database
        connection if it is open.

        Args:
            exc_type (type): The exception type, if any.
            exc_val (Exception): The exception value, if any.
            exc_tb (traceback): The traceback object, if any.
        """
        if self.conn:
            self.conn.close()
            self.logger.database(f"Connection to SQLite database '{self.db_file}' closed")
