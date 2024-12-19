from __future__ import annotations

from marshmallow import fields
from marshmallow import Schema
from marshmallow import validate


class BaseModelSchema(Schema):
    """
    A base schema for validating the essential metadata of a model.

    This schema defines the fundamental fields that must be provided for any model
    being registered or manipulated in the system. These fields are the minimum required
    information for model identification and versioning.

    Fields:
        name (str): The name of the model. This field is required and must be a non-empty string.
        version (str): The version of the model. This field is required and must be a non-empty string.
    """

    name = fields.Str(required=True, validate=validate.Length(min=1))
    version = fields.Str(required=True, validate=validate.Length(min=1))


class ModelSchema(BaseModelSchema):
    """
    A schema for validating comprehensive model metadata.

    This schema extends `BaseModelSchema` and includes additional fields to capture
    more detailed information about the model, such as its description, framework, version,
    training data, hyperparameters, evaluation metrics, author, status, and labels. These fields
    provide a more complete context of the model's usage, development, and deployment status.

    Fields:
        features: Features of model that trained with.
        description (str, optional): A brief description of the model. Defaults to "No description."
        framework (str, optional): The framework used to build the model (e.g., "scikit-learn", "PyTorch", "TensorFlow").
            Defaults to "No framework specified."
        framework_version (str, optional): The version of the framework used. Defaults to "No framework version specified."
        training_data (str, optional): Information about the training data used. Defaults to "No training data specified."
        hyperparameters (str, optional): Hyperparameters used for training, which can be serialized as JSON.
            Defaults to "No hyperparameters specified."
        evaluation_metrics (str, optional): Evaluation metrics of the model, which can be serialized as JSON.
            Defaults to "No evaluation metrics specified."
        model_author (str, optional): The author of the model. Defaults to "ADO-AI."
        status (str, optional): The current status of the model (e.g., "deployed", "archived", "under review", "special-use").
            Defaults to "under review."
        labels (list of str, optional): Labels associated with the model for categorization. Defaults to ["No Label"].

    Args:
        BaseModelSchema (Schema): Inherits from the base schema for model metadata.
    """

    features = fields.Str(required=True, validate=validate.Length(min=1))  # Should be list time is short.
    description = fields.Str(required=False, validate=validate.Length(min=1), missing="No description.")
    framework = fields.Str(required=False, validate=validate.Length(min=1), missing="No framework specified.")
    framework_version = fields.Str(required=False, validate=validate.Length(min=1), missing="No framework version specified.")
    training_data = fields.Str(required=False, validate=validate.Length(min=1), missing="No training data specified.")
    hyperparameters = fields.Str(required=False, missing="No hyperparameters specified")  # Can be JSON serialized
    evaluation_metrics = fields.Str(required=False, missing="No evaluation metrics specified")  # Can be JSON serialized
    model_author = fields.Str(required=False, validate=validate.Length(min=1), missing="ADO-AI")
    status = fields.Str(required=False, validate=validate.OneOf(["deployed", "archived", "under review", "special-use"]), missing="under review")
    labels = fields.List(fields.Str(), required=False, missing=["No Label"])


class AddDeleteModelSchema(ModelSchema):
    """
    A schema for validating model metadata when adding a new model.

    This schema extends `ModelSchema` and adds a required `file_path` field to specify
    the path of the model file being uploaded when a new model is added to the system.
    This field ensures that a valid file path is provided for the model upload process.

    Fields:
        file_path (str): The path to the model file being uploaded. This field is required
            and must be a non-empty string.

    Args:
        ModelSchema (ModelSchema): Inherits from the schema that includes comprehensive
        model metadata.
    """

    file_path = fields.Str(required=True, validate=validate.Length(min=1))


class FetchModelSchema(ModelSchema):
    """
    Schema for fetching model details from the model registry.

    This schema is used to validate the input when fetching a model's details from the registry.
    It ensures that the required fields are provided and conform to expected constraints.

    Args:
        ModelSchema (marshmallow_sqlalchemy.ModelSchema): Base schema class for SQLAlchemy models.

    """

    uploaded_file_name = fields.Str(required=True, validate=validate.Length(min=1))
    file_path = fields.Str(required=True, validate=validate.Length(min=1))


class UpdateModelSchema(ModelSchema):
    """
    Schema for updating model details in the model registry.

    This schema is used to validate the input when updating a model's metadata or other attributes in the registry.
    All fields are optional and can be omitted if they are not being updated.

    Args:
        ModelSchema (marshmallow_sqlalchemy.ModelSchema): Base schema class for SQLAlchemy models.

    """

    file_path = fields.Str(required=False, validate=validate.Length(min=1), missing=None)
    description = fields.Str(required=False, validate=validate.Length(min=1), missing=None)
    framework = fields.Str(required=False, validate=validate.Length(min=1), missing=None)
    framework_version = fields.Str(required=False, validate=validate.Length(min=1), missing=None)
