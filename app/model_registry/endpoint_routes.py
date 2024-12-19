from __future__ import annotations

import os  # noqa

import model_schema as schema
from flask import Blueprint
from flask import jsonify
from flask import request
from flask_executor import Executor
from http_status_enums import HTTPStatus
from marshmallow import ValidationError  # noreorder # noqa
from registry import ModelRegistry  # noreorder # noqa
from logger.logger import ColorLogger as Logger  # noreorder # noqa


model_bp = Blueprint("model_bp", __name__)

database = "database" + os.sep + "model_database_file.db"
registry_logger = Logger(log_file="logs" + os.sep + "registry_endpoint_logger.log", debug_mode=False)
registry = ModelRegistry(database, registry_logger)
executor = Executor()


class BackgroundTasks:
    """
    A class to encapsulate all background tasks related to model management.
    """

    @staticmethod
    def upload_model_task(data):
        """
        Background task to upload the model.
        """
        success, message = registry.insert_model(**data)
        return success, message

    @staticmethod
    def remove_model_task(data):
        """
        Background task to remove the model.
        """
        success, message = registry.delete_model(**data)
        return success, message

    @staticmethod
    def update_model_task(data):
        """
        Background task to update the model.
        """
        try:
            success, message = registry.update_model(
                name=data["name"],
                version=data["version"],
                description=data.get("description"),
                framework=data.get("framework"),
                framework_version=data.get("framework_version"),
                model_author=data.get("model_author"),
                status=data.get("status"),
                labels=data.get("labels"),
            )

            return success, message
        except Exception as e:
            message = f"Exception occured at background updating model {e}"
            return None, message

    @staticmethod
    def fetch_model_task(name, version, download=False, download_path="Downloads"):
        """
        Background task to fetch a model by name and version.
        """
        try:
            data, message = registry.fetch_model(name, version, download=download, download_path=download_path)
            if data:
                return data, message
            else:
                return data, message
        except Exception as e:
            message = f"Exception occured at background downloading model {e}"
            registry.logger.critical(message)
            return None, message


# Define routes


@model_bp.route("/status", methods=["GET"])
def status():
    response_code = HTTPStatus.OK
    registry_logger.endpoint(f"Status request recieved. Response:{response_code}")
    return jsonify({"message": "ado-flow up and running.", "Status": "OK"}), response_code.value


@model_bp.route("/upload_model", methods=["POST"])
def upload_model():
    """
    Upload a new model to the registry.

    This endpoint allows the user to upload a new model to the model registry.
    The model is identified by its `name` and `version`, and various details such as description,
    framework, framework version, model author, status, and labels can be provided.

    ---
    tags:
      - Models
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                description: The name of the model.
                example: "CustomModel"
              version:
                type: string
                description: The version of the model.
                example: "1.0"
              description:
                type: string
                description: A brief description of the model.
                example: "Updated model description."
              framework:
                type: string
                description: The framework used for the model (e.g., "scikit-learn", "PyTorch", "TensorFlow").
                example: "PyTorch"
              framework_version:
                type: string
                description: The version of the framework.
                example: "1.8"
              model_author:
                type: string
                description: The author of the model.
                example: "Jane Doe"
              status:
                type: string
                description: The status of the model (e.g., "deployed", "archived", "under review").
                example: "archived"
              labels:
                type: array
                items:
                  type: string
                description: A list of labels associated with the model.
                example: ["updated_label"]
    responses:
      200:
        description: Model uploaded successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Confirmation message indicating the model was uploaded successfully.
      203:
        description: Model was not uploaded due to logical constraints.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Request was correct, but the system did not upload the model entry for logical reasons.
      400:
        description: Validation error or bad request.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message indicating what validation failed.
      500:
        description: Failed to upload model due to a server error.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message indicating a server-side issue that prevented the upload.
    """
    try:
        data = schema.AddDeleteModelSchema().load(request.json)
        future = executor.submit(BackgroundTasks.upload_model_task, data)
        success, message = future.result()
        response_code = HTTPStatus.OK
        registry_logger.endpoint(f"Uploading model. {message} response:{response_code}")
        if success:
            return jsonify({"message": message, "response:": response_code.value}), response_code.value
        return jsonify({"message": message, "response:": HTTPStatus.DECLINED.value}), HTTPStatus.DECLINED.value
    except ValidationError as err:
        registry_logger.endpoint(f"Uploading model. {err.messages} response:{HTTPStatus.BAD_REQUEST}")
        return jsonify({"message": err.messages, "response:": str(HTTPStatus.BAD_REQUEST.value)}), HTTPStatus.BAD_REQUEST.value


@model_bp.route("/fetch_model", methods=["GET"])
def fetch_model():
    """
    Fetch a model from the registry by name and version.

    This endpoint retrieves a model from the model registry by its name and version.
    It expects the `name` and `version` parameters to be provided in the query string.
    If the model is found, its details are returned; otherwise, an error message is provided.

    ---
    tags:
      - Models
    parameters:
      - in: query
        name: name
        required: true
        schema:
          type: string
        description: The name of the model to fetch from the registry.
      - in: query
        name: version
        required: true
        schema:
          type: string
        description: The version of the model to fetch from the registry.
    responses:
      200:
        description: Model retrieved successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  description: The name of the model.
                version:
                  type: string
                  description: The version of the model.
                description:
                  type: string
                  description: The description of the model.
                framework:
                  type: string
                  description: The machine learning framework used by the model.
                framework_version:
                  type: string
                  description: The version of the machine learning framework.
                model_author:
                  type: string
                  description: The author of the model.
                status:
                  type: string
                  description: The status of the model.
                labels:
                  type: array
                  items:
                    type: string
                  description: List of labels associated with the model.
      400:
        description: Model name and version are required.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message indicating missing parameters.
      404:
        description: Model not found.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message indicating that the model was not found.
    """
    name = request.json.get("name")
    version = request.json.get("version")

    if not name or not version:
        return jsonify({"Error": "Model name and version are required", "response:": 400})

    future = executor.submit(BackgroundTasks.fetch_model_task, name, version)
    data_from_database, message = future.result()
    if data_from_database is None:
        response_code = HTTPStatus.BAD_REQUEST.value
        registry_logger.endpoint(f"Could not fetch data. {message} response:{response_code}")
        return jsonify({"data": data_from_database, "message": message, "response:": response_code})
    else:
        response_code = HTTPStatus.OK.value
        registry_logger.endpoint(f"Fetch successful fetched data {data_from_database}. {message} response:{response_code}")
        return jsonify({"model_metadata": data_from_database, "message": message, "response:": response_code})


@model_bp.route("/fetch_and_download_model", methods=["GET"])
def fetch_and_download_model():
    """
    Fetch and download a model from the registry by name and version.

    This endpoint retrieves a model from the model registry by its name and version,
    and also downloads the model file if it is available. It expects the `name` and `version`
    parameters to be provided in the request body. If the model is found, its details and file
    download information are returned; otherwise, an error message is provided.

    ---
    tags:
      - Models
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                description: The name of the model to fetch and download from the registry.
                example: "RandomForestClassifier"
              version:
                type: string
                description: The version of the model to fetch and download from the registry.
                example: "1.0"
    responses:
      200:
        description: Model fetched and downloaded successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                model_metadata:
                  type: object
                  description: Metadata of the fetched model.
                message:
                  type: string
                  description: Confirmation message indicating the model was fetched and downloaded successfully.
      400:
        description: Model name and version are required.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message indicating missing parameters.
      404:
        description: Model not found or could not be downloaded.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message indicating that the model was not found or the download failed.
    """
    name = request.json.get("name")
    version = request.json.get("version")
    download_path = request.json.get("download_path", "Downloads")

    if not name or not version:
        return jsonify({"Error": "Model name and version are required", "response:": 400})

    future = executor.submit(BackgroundTasks.fetch_model_task, name, version, True, download_path)
    data_from_database, message = future.result()
    if data_from_database is None:
        response_code = HTTPStatus.BAD_REQUEST.value
        registry_logger.endpoint(f"Could not fetch data. {message} response:{response_code}")
        return jsonify({"data": data_from_database, "message": message, "response:": response_code})
    else:
        response_code = HTTPStatus.OK.value
        registry_logger.endpoint(f"Fetch successful fetched data {data_from_database}. {message} response:{response_code}")
        return jsonify({"model_metadata": data_from_database, "message": message, "response:": response_code})


@model_bp.route("/update_model_entry", methods=["PUT"])
def update_model_entry():
    """
    Update an existing model in the registry.

    This endpoint allows the user to update an existing model's details in the model registry.
    The model is identified by its `name` and `version`, and various fields can be updated,
    including description, framework, framework version, model author, status, and labels.

    ---
    tags:
      - Models
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                description: The name of the model.
                example: "CustomModel"
              version:
                type: string
                description: The version of the model.
                example: "1.0"
              description:
                type: string
                description: A brief description of the model.
                example: "Updated model description."
              framework:
                type: string
                description: The framework used for the model (e.g., "scikit-learn", "PyTorch", "TensorFlow").
                example: "PyTorch"
              framework_version:
                type: string
                description: The version of the framework.
                example: "1.8"
              model_author:
                type: string
                description: The author of the model.
                example: "Jane Doe"
              status:
                type: string
                description: The status of the model (e.g., "deployed", "archived", "under review").
                example: "archived"
              labels:
                type: array
                items:
                  type: string
                description: A list of labels associated with the model.
                example: ["updated_label"]
    responses:
      200:
        description: Model updated successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Confirmation message indicating the model was updated successfully.
      400:
        description: Validation error or bad request.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message indicating what validation failed.
      500:
        description: Failed to update model due to a server error.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message indicating a server-side issue that prevented the update.
    """
    try:
        data = schema.UpdateModelSchema().load(request.json)
        future = executor.submit(BackgroundTasks.update_model_task, data)

        success, message = future.result()
        response_code = HTTPStatus.OK if success else HTTPStatus.DECLINED
        registry_logger.endpoint(f"Updating model. {message} response:{response_code}")
        return jsonify({"message": message, "response:": response_code.value}), response_code.value
    except ValidationError as err:
        registry_logger.endpoint(f"Updating model. {err.messages} response:{HTTPStatus.BAD_REQUEST.value}")
        return jsonify({"message": err.messages, "response:": HTTPStatus.BAD_REQUEST.value}), HTTPStatus.BAD_REQUEST.value


@model_bp.route("/remove_model", methods=["DELETE"])
def remove_model():
    """
    Delete a model from the registry by name and version.

    This endpoint allows the user to delete a model from the registry by specifying the model's `name` and `version`.
    If both the name and version are provided and valid, the specified model is removed from the registry.

    ---
    tags:
      - Models
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                description: The name of the model.
                example: "CustomModel"
              version:
                type: string
                description: The version of the model.
                example: "1.0"
    responses:
      200:
        description: Model deleted successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Confirmation message indicating the model was deleted successfully.
      400:
        description: Model name and version are required.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message indicating that the model name and version are required.
      500:
        description: Failed to delete model due to a server error.
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message indicating a server-side issue that prevented the deletion.
    """

    data = schema.BaseModelSchema().load(request.json)

    name = data["name"]
    version = data["version"]

    if not name or not version:
        return jsonify({"error": "Model name and version are required", "response:": HTTPStatus.BAD_REQUEST.value}), HTTPStatus.BAD_REQUEST.value

    future = executor.submit(BackgroundTasks.remove_model_task, data)

    success, message = future.result()
    response_code = HTTPStatus.OK if success else HTTPStatus.DECLINED
    registry_logger.endpoint(f"Updating model. {message} response:{response_code}")
    return jsonify({"message": message, "response:": response_code.value}), response_code.value


@model_bp.route("/export_model_csv", methods=["GET"])
def export_to_csv():
    """
    Export the list of models in the registry to a CSV file.

    This endpoint exports all models in the registry to a CSV file. The exported file contains
    details of each model, including its metadata and associated information. If the export is
    successful, a confirmation message is returned. If there is an error, an appropriate error
    message is provided.

    ---
    tags:
      - Models
    responses:
      200:
        description: Models exported to CSV successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Confirmation message indicating the models were exported successfully.
                response:
                  type: integer
                  description: HTTP status code.
      400:
        description: Failed to export models to CSV.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  description: Error message indicating the failure reason.
                response:
                  type: integer
                  description: HTTP status code.
    """
    success, message = registry.export_to_csv()
    response_code = HTTPStatus.OK if success else HTTPStatus.BAD_REQUEST
    return jsonify({"message": message, "response:": response_code.value}), response_code.value
