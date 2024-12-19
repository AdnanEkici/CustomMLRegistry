from __future__ import annotations

import csv
import os
import sys
from datetime import datetime
from sqlite3 import Error

from marshmallow import ValidationError


# Correcting import paths to ensure SQLiteDB is properly imported
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from model_registry.model_schema import FetchModelSchema  # noreorder # noqa
from model_registry.model_schema import BaseModelSchema  # noreorder # noqa
from model_registry.sqllite_db import SQLiteDB  # noreorder # noqa
from model_registry.storage_manager import GCloudStorageManager  # noreorder # noqa
from logger.logger import ColorLogger  # noreorder # noqa


class ModelRegistry:
    """
    A class to manage the registration and update of machine learning models in a database.

    This class provides functionality to add, update, and manage metadata and labels
    for machine learning models stored in a database. It also supports the dynamic updating
    of model fields and labels, ensuring data integrity and consistency.
    """

    def __init__(
        self,
        db_file: str,
        logger: ColorLogger,
        bucket_name: str | None = None,
        query_path: str = os.path.join(current_dir, "model_registry.sql"),
    ):
        """
        Initialize the ModelRegistry with a database file and SQL query file path.

        Args:
            db_file (str): The path to the SQLite database file where model metadata is stored.
            query_path (str, optional): The path to the SQL file containing SQL queries for managing the model registry.
                Defaults to the 'model_registry.sql' file in the current directory.
        """

        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        self.db_file = db_file
        self.logger = logger
        self.logger.info(f"Using sql query from {query_path}")
        self.logger.info(f"Using database file {db_file}")

        self.sql_queries = self.__load_sql_queries(query_path)
        self.storage_manager = GCloudStorageManager(bucket_name=bucket_name, logger=self.logger)

    def create_tables(self):
        """
        Create the necessary tables for the model registry in the SQLite database.

        This method creates three tables:
        - `model_metadata`: Stores metadata for each model, such as name, version, description, framework, etc.
        - `labels`: Stores distinct labels that can be associated with models.
        - `model_labels`: A junction table that links models to their associated labels.

        If the tables already exist, the method does nothing. If an error occurs during table creation,
        it prints the error message.
        """
        with SQLiteDB(self.db_file, logger=self.logger) as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(self.sql_queries["Create the model_metadata table"])
                cursor.execute(self.sql_queries["Create the labels table"])
                cursor.execute(self.sql_queries["Create the model_labels table"])
                self.logger.database("Tables created or already exist.")
            except Error as e:
                self.logger.database_error(f"Error creating tables: {e}")

    def insert_model(
        self,
        name: str,
        version: str,
        file_path: str,
        description: str,
        framework: str,
        framework_version: str,
        training_data: str,
        hyperparameters: str | dict,
        evaluation_metrics: str | dict,
        model_author: str,
        status: str,
        features: str,
        labels: list,
    ):
        """
        Insert a new model into the model registry, including its metadata and associated labels.

        This method adds a new model entry to the `model_metadata` table and associates it with labels
        in the `model_labels` table. It also attempts to upload the model file to cloud storage. If the
        file upload fails, the database entry is rolled back to maintain consistency.

        Args:
            name (str): The name of the model.
            version (str): The version of the model.
            file_path (str): The local file path of the model file.
            description (str): A brief description of the model.
            framework (str): The framework used to create the model (e.g., "scikit-learn", "PyTorch").
            framework_version (str): The version of the framework used.
            training_data (str): Description or source of the training data used.
            hyperparameters (str): Hyperparameters used in the model, typically as a JSON string.
            evaluation_metrics (str): Evaluation metrics for the model, typically as a JSON string.
            model_author (str): The author of the model.
            status (str): The status of the model (e.g., "deployed", "archived", "under review", "special-use").
            labels (list): A list of labels (tags) associated with the model.

        Raises:
            FileNotFoundError: If the specified model file path does not exist.

        Returns:
            bool: True if the model is inserted and uploaded successfully, False otherwise.
        """
        try:
            BaseModelSchema().load({"name": name, "version": version})
        except ValidationError:
            message = "Model name and version must be given."
            self.logger.registry_error("Model name and version must be given.")
            return False, message

        uploaded_file_name = self.__generate_storage_model_name(name=name, version=version, file_path=file_path)

        with SQLiteDB(self.db_file, logger=self.logger) as conn:
            try:
                cursor = conn.cursor()
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                last_updated = created_at

                cursor.execute(
                    self.sql_queries["Insert model metadata"],
                    (
                        name,
                        version,
                        file_path,
                        description,
                        created_at,
                        framework,
                        framework_version,
                        training_data,
                        hyperparameters,
                        evaluation_metrics,
                        model_author,
                        last_updated,
                        uploaded_file_name,
                        features,
                        status,
                    ),
                )
                model_id = cursor.lastrowid

                for label in labels:
                    cursor.execute(self.sql_queries["Insert label if it does not exist"], (label,))
                    cursor.execute(self.sql_queries["Select label id by label name"], (label,))
                    label_id = cursor.fetchone()[0]  # Get the label ID
                    cursor.execute(self.sql_queries["Insert model-label relationship"], (model_id, label_id))

                # Attempt to upload the model file to cloud storage
                try:
                    self.storage_manager.upload_file(source_filename=file_path, destination_filename=uploaded_file_name) and conn.commit()
                    message = f"Model '{name}' version '{version}' inserted and uploaded successfully with labels: {labels}."
                    self.logger.registry(message)
                    return True, message

                except Exception as upload_error:
                    conn.rollback()
                    message_error = f"Error while uploading file to cloud storage: {upload_error}"
                    message_warning = f"Model '{name}' version '{version}' entry rolled back from the database due to upload failure."
                    self.logger.storage_error(message_error)
                    self.logger.warning(message_warning)
                    return False, (message_error + " " + message_warning)

            except Error as db_error:
                message = f"Error inserting data into the database: {db_error}"
                self.logger.database_error(message)
                return False, message

    def fetch_model(self, name, version, download: bool = False, download_path: str = "Downloads"):
        """
        Fetch a model's metadata and associated labels from the database based on the model's name and version.

        This method retrieves a model's metadata from the `model_metadata` table and its associated labels
        from the `model_labels` table. It then validates the fetched data using the `FetchModelSchema` schema
        and returns it as a dictionary. If the model is not found, it returns `None`.

        Args:
            name (str): The name of the model to fetch.
            version (str): The version of the model to fetch.
            download (bool): If enabled will download model from google cloud.

        Returns:
            dict or None: A dictionary containing the model's validated metadata and associated labels if found,
                        otherwise `None`.
        """
        with SQLiteDB(self.db_file, logger=self.logger) as conn:
            try:
                cursor = conn.cursor()

                cursor.execute(self.sql_queries["Select model by name and version"], (name, version))
                rows = cursor.fetchall()

                if rows:
                    model_schema = FetchModelSchema()
                    for row in rows:
                        model_id = row["id"]
                        cursor.execute(self.sql_queries["Select labels for a given model"], (model_id,))
                        labels = [label["label"] for label in cursor.fetchall()]

                        model_dict = dict(row)
                        model_dict["labels"] = labels
                        validated_data = model_schema.dump(model_dict)
                        message = f"Model '{name}' and version '{version}' has been found."
                        self.logger.registry(message)

                        if download:
                            try:
                                uploaded_file_name = model_dict["uploaded_file_name"]
                                success, download_message = self.storage_manager.download_file(
                                    filename=uploaded_file_name, download_path=download_path
                                )
                                if not success:
                                    return None, download_message
                            except Exception as e:
                                download_message = f"Exception {e} has been occured while downloading {uploaded_file_name} from google cloud."
                                self.logger.registry_error(download_message)
                                return None, download_message

                        return validated_data, message
                else:
                    message = f"No models found for name '{name}' and version '{version}'."
                    self.logger.registry_error(message)
                    return None, message
            except Error as e:
                message = f"Error fetching data: {e}"
                self.logger.database_error()
                return None, message

    def __generate_storage_model_name(self, name, version, file_path=None):
        """
        Generate a unique storage file name for a model based on its name, version, and file extension.

        This method creates a standardized name for storing the model file in cloud storage or other systems.
        The generated name is based on the model's name and version, preserving the original file extension.

        Args:
            name (str): The name of the model.
            version (str): The version of the model.
            file_path (str): The local file path of the model file, used to extract the file extension.

        Returns:
            str: A string representing the generated storage file name in the format 'model__<name>__<version>.<extension>'.
        """
        if file_path is not None:
            _, file_extension = os.path.splitext(file_path)
        file_extension = ".joblib"

        return f"model__{name}__{version}{file_extension}"

    def update_model(self, name, version, description=None, framework=None, framework_version=None, model_author=None, status=None, labels=None):
        """
        Update a model's metadata and labels in the model registry.

        This method updates the provided fields of a model in the `model_metadata` table
        and its associated labels in the `model_labels` table. Only the fields that are not
        `None` are updated in the database. If labels are provided, it replaces existing labels
        with the new ones.

        Args:
            name (str): The name of the model to update.
            version (str): The version of the model to update.
            description (str, optional): New description of the model. Defaults to None.
            framework (str, optional): New framework of the model (e.g., "scikit-learn", "PyTorch"). Defaults to None.
            framework_version (str, optional): New version of the framework used. Defaults to None.
            model_author (str, optional): New author of the model. Defaults to None.
            status (str, optional): New status of the model (e.g., "deployed", "archived"). Defaults to None.
            labels (list, optional): A list of new labels to associate with the model. Defaults to None.

        Returns:
            bool: True if the model is updated successfully, False otherwise.
        """
        # List of allowed fields to update and their provided values
        update_fields = {
            "description": description,
            "framework": framework,
            "framework_version": framework_version,
            "model_author": model_author,
            "status": status,
        }

        # Filter out fields that are None
        fields_to_update = {k: v for k, v in update_fields.items() if v is not None}
        # If no fields are provided for update, return early
        if not fields_to_update and labels is None:
            message = "No fields provided for update."
            self.logger.warning("No fields provided for update.")
            return False, message

        # Dynamically build the SQL query for updating only the provided fields
        set_clause = ", ".join([f"{field} = ?" for field in fields_to_update.keys()])
        sql_query = f"UPDATE model_metadata SET {set_clause}, last_updated = ? WHERE name = ? AND version = ?;"
        self.logger.debug(f"SQL querry for update ==> {sql_query}")

        # Prepare the parameters for the SQL query
        params = list(fields_to_update.values()) + [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, version]

        with SQLiteDB(self.db_file, logger=self.logger) as conn:
            try:
                cursor = conn.cursor()

                # Execute the dynamically generated SQL query
                cursor.execute(sql_query, params)

                # Handle updating labels if provided
                if labels is not None:
                    # Fetch the model ID based on name and version
                    cursor.execute(self.sql_queries["Select model id by name and version"], (name, version))

                    # if cursor.fetchone() is None:
                    #     return False
                    model_id_tuple = cursor.fetchone()

                    if model_id_tuple is None:
                        message = "Could not found any related model for given model name and version."
                        self.logger.warning(message)
                        return False, message

                    model_id = model_id_tuple[0]

                    cursor.execute(self.sql_queries["Delete labels for a given model"], (model_id,))

                    # Insert new labels
                    for label in labels:
                        # Insert label if it does not exist
                        cursor.execute(self.sql_queries["Insert label if it does not exist"], (label,))
                        # Fetch the label ID
                        cursor.execute(self.sql_queries["Select label id by label name"], (label,))
                        label_id = cursor.fetchone()[0]
                        # Insert the model-label relationship
                        cursor.execute(self.sql_queries["Insert model-label relationship"], (model_id, label_id))

                conn.commit()  # Commit the transaction
                message = f"Model '{name}' version '{version}' updated successfully."
                self.logger.registry(message)
                return True, message
            except Error as e:
                message = f"Error updating data: {e}"
                self.logger.database_error(message)
                return False, message

    def delete_model(self, name, version):
        """
        Delete a model from the model_metadata table and its associated labels, and also delete the model file from cloud storage.

        This method deletes a model entry from the `model_metadata` table based on the provided
        name and version. It also removes any associated labels from the `model_labels` table
        and attempts to delete the corresponding file from cloud storage. If any step fails, it
        rolls back all changes to maintain consistency.

        Args:
            name (str): The name of the model to delete.
            version (str): The version of the model to delete.

        Returns:
            bool: True if the model is deleted successfully, False otherwise.
        """
        with SQLiteDB(self.db_file, logger=self.logger) as conn:
            try:
                cursor = conn.cursor()

                # Fetch the model file path before deletion
                cursor.execute(self.sql_queries["Select model by name and version"], (name, version))
                model = cursor.fetchone()

                if model is None:
                    message = f"Error: No model found with name '{name}' and version '{version}'."
                    self.logger.registry_error(message)
                    return False, message

                file_to_be_removed_from_cloud = self.__generate_storage_model_name(name=name, version=version)

                # Delete labels associated with the model
                cursor.execute(self.sql_queries["Select model id by name and version"], (name, version))
                model_id = cursor.fetchone()[0]
                cursor.execute(self.sql_queries["Delete labels for a given model"], (model_id,))

                # Delete the model from the database
                cursor.execute(self.sql_queries["Delete a model by name and version"], (name, version))

                # Attempt to delete the file from cloud storage
                if self.storage_manager.delete_file(file_to_be_removed_from_cloud):
                    conn.commit()  # Commit the transaction if everything is successful
                    message = f"Model '{name}' version '{version}' deleted successfully from database and cloud storage."
                    self.logger.registry(message)
                    return True, message
                else:
                    # Rollback the transaction if the cloud deletion fails
                    conn.rollback()
                    message_error = f"Error: Failed to delete model file '{file_to_be_removed_from_cloud}' from cloud storage."
                    message_warning = "Rolling back database changes."
                    self.logger.storage_error(message_error)
                    self.logger.warning()
                    return False, (message_error + " " + message_warning)

            except Error as e:
                conn.rollback()  # Rollback the transaction if any database operation fails
                message = f"Error deleting data: {e}"
                self.logger.database_error(message)
                return False, message

    def export_to_csv(self, output_file="models_export.csv"):
        """Export all data in the model_metadata table to a CSV file"""
        models = []  # Initialize list to store all models
        headers = self.__get_column_names_from_db(table_name="model_metadata")

        with SQLiteDB(self.db_file, logger=self.logger) as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(self.sql_queries["Select all models"])
                rows = cursor.fetchall()

                if rows:
                    for row in rows:
                        model_id = row[0]
                        cursor.execute(self.sql_queries["Select labels for a given model"], (model_id,))
                        labels = [label[0] for label in cursor.fetchall()]
                        model_data = list(row) + [", ".join(labels)]
                        models.append(model_data)

                    with open(output_file, "w", newline="") as csvfile:
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow(headers)
                        csv_writer.writerows(models)
                    message = f"Data exported successfully to {output_file}"
                    self.logger.registry(message)
                    return True, message
                else:
                    message = "No data found in the 'model_metadata' table."
                    self.logger.registry_error(message)
                    return False, message
            except Error as e:
                message = f"Error exporting data to CSV: {e}"
                self.logger.critical(message)
                return False, message

    def __load_sql_queries(self, filepath):
        """
        Load SQL queries from a file and store them in a dictionary.

        This method reads an SQL file containing multiple queries separated by semicolons (`;`) and
        extracts each query into a dictionary using comments in the file as keys. It is assumed that
        each SQL statement is preceded by a comment that indicates the query's name (e.g., `-- Query Name`).

        Args:
            filepath (str): The path to the SQL file containing the queries.

        Returns:
            dict: A dictionary where each key is the name of a query (extracted from comments),
                and each value is the corresponding SQL query string.
        """
        queries = {}
        with open(filepath) as file:
            sql_script = file.read()
            sql_commands = sql_script.split(";")

            for command in sql_commands:
                if command.strip():
                    lines = command.strip().splitlines()
                    query_name = lines[0].strip("-- ").strip()
                    query_sql = "\n".join(lines[1:]).strip()
                    queries[query_name] = query_sql
        return queries

    def __get_column_names_from_db(self, table_name: str) -> list[str]:
        """
        Fetch column names for a specific table in the SQLite database.

        Args:
            table_name (str): Name of the table to fetch column names from.

        Returns:
            list[str]: A list of column names.
        """
        with SQLiteDB(self.db_file, logger=self.logger) as conn:
            cursor = conn.cursor()

            cursor.execute(f"PRAGMA table_info({table_name});")
            columns_info = cursor.fetchall()

            # Column names are in the second position of each row in PRAGMA output
            column_names = [info[1] for info in columns_info]
            conn.close()
            return column_names
