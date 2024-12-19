from __future__ import annotations

import argparse
import json
import os
import random
import traceback
from abc import abstractmethod
from functools import wraps
from typing import Final

import joblib
import numpy as np
import pandas as pd
import requests
import yaml
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from app.trainer.dataset_processor import DatasetProcessor

from app.logger.logger import ColorLogger as Logger  # noreorder # noqa


adjectives = [
    "Silly",
    "Wobbly",
    "Fluffy",
    "Grumpy",
    "Crazy",
    "Jumpy",
    "Lazy",
    "Smelly",
    "Nerdy",
    "Funky",
    "Giggly",
    "Clumsy",
    "Sneaky",
    "Goofy",
    "Sassy",
    "Fuzzy",
    "Puffy",
    "Zippy",
    "Wacky",
    "Bouncy",
    "Dizzy",
    "Jolly",
    "Loopy",
    "Muddy",
    "Nutty",
    "Perky",
    "Quirky",
]

nouns = [
    "Penguin",
    "Noodle",
    "Pickle",
    "Muffin",
    "Banana",
    "Nugget",
    "Monkey",
    "Pancake",
    "Waffle",
    "Pumpkin",
    "Biscuit",
    "Unicorn",
    "Doodle",
    "Sloth",
    "Kitten",
    "Panda",
    "Duckling",
    "Wombat",
    "Bumblebee",
    "Donut",
    "Cupcake",
    "Taco",
    "Ostrich",
    "Dinosaur",
    "Butterfly",
    "Llama",
    "Potato",
    "Hamster",
    "Octopus",
]


def generate_experiment_name():
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    experiment_name = f"{adjective}_{noun}"
    return experiment_name


class Trainer:
    PROCESSED_DATASET_SAVE_PATH: Final = "saved_datasets"
    MODEL_SAVE_PATH: Final = "saved_models"
    YAML_PRETTY_PRINT: Final = 4
    SUPPORTED_REGISTRY_LIST: Final = ["ado-flow"]

    def __init__(self, train_config: dict = None, logger=None):
        self.train_config = train_config

        # PARSING SUB CONFIGS
        self.registry_meta_data = self.train_config["meta_data"]
        self.trainer_config = self.train_config["train_config"]

        # PARSING TRAIN CONFIGS
        dataset_params = self.trainer_config["dataset"]
        train_params = self.trainer_config["train"]
        registry_config = trainer_config["registry"]

        self.version = self.registry_meta_data.get("version", None)

        if self.version is None:
            raise ValueError("Model version can not be NONE !")

        if experiment_name is None:
            self.experiment_name = generate_experiment_name()

        # PARSE REGISTRY CONFIG
        registry_name = registry_config.get("name", None)
        registry_url = registry_config.get("url", None)
        # REGISTRY VARIABLES
        self.registry_name = registry_name
        self.registry_url = registry_url

        # PARSING TRAIN CONFIG
        features = train_params.get("features", None)
        train_validation_split_ratio = train_params.get("train_validation_split_ratio", 0.2)
        prediction_target = train_params.get("prediction_target", None)
        deflection = train_params.get("deflection", 0)
        random_state = train_params.get("random_state", 42)
        saved_model_path = train_params.get("saved_model_path", None)
        hyperparameters = train_params.get("hyperparameters", None)

        # TRAINING VARIABLES
        self.hyperparameters = hyperparameters
        self.registry_meta_data["hyperparameters"] = json.dumps(self.hyperparameters)
        self.features = (
            ["age", "gender_Female", "Recency", "Frequency", "Monetary", "annual_income", "purchase_amount"] if features is None else features
        )
        self.random_state = random_state
        self.train_validation_split_ratio = train_validation_split_ratio
        self.deflection = deflection
        self.target = prediction_target

        # PARSING DATASET CONFIG
        raw_dataset_csv = dataset_params.get("raw_dataset_csv", None)
        numerical_columns = dataset_params.get("numerical_columns", None)
        categorical_columns = dataset_params.get("categorical_columns", None)
        save_datasets_as_csv = dataset_params.get("save_datasets_as_csv", None)

        # DATASET VARIABLES
        self.raw_dataset_csv = raw_dataset_csv
        self.numerical_columns = numerical_columns
        self.categorical_columns = categorical_columns

        # EXPORT OPTIONS
        self.save_datasets = save_datasets_as_csv
        self.model_save_path = saved_model_path

        # MISC
        self.experiment_name = experiment_name
        self.logger = logger

        # INNER VARIABLES
        self.model = None
        self.train_dataframe = None
        self.validation_dataframe = None
        self.test_dataframe = None

        if "training_data" in self.registry_meta_data:
            self.registry_meta_data["training_data"] = self.registry_meta_data["training_data"] + f" Dataset path: {self.raw_dataset_csv}"

        self.registry_meta_data["features"] = json.dumps(self.features)

        self.data_processor = DatasetProcessor(
            csv_path=self.raw_dataset_csv,
            features=self.features,
            numerical_columns=self.numerical_columns,
            categorical_columns=self.categorical_columns,
            target_column=self.target,
        )

        self.train_dataframe, self.test_dataframe = self.data_processor.process_dataset(save=False)

    def prepare_data(self):
        """Prepares the training and validation datasets by selecting features, splitting the data,
        and optionally saving the processed datasets.

        Returns:
            tuple: The training and validation sets for both features (X) and target (y).
        """
        # Selecting relevant features and target
        X = self.train_dataframe[self.features]
        y = self.train_dataframe[self.target]

        # Split the data into training and validation sets (80% train, 20% validation)
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=self.train_validation_split_ratio, random_state=self.random_state)

        # Store the datasets
        self.train_dataframe = pd.concat([X_train, y_train], axis=1)
        self.validation_dataframe = pd.concat([X_val, y_val], axis=1)

        # Optionally save the datasets
        if self.save_datasets:
            os.makedirs(Trainer.PROCESSED_DATASET_SAVE_PATH, exist_ok=True)
            self.train_dataframe.to_csv(Trainer.PROCESSED_DATASET_SAVE_PATH + os.sep + f"train_dataset_version_{self.version}.csv", index=False)
            self.validation_dataframe.to_csv(
                Trainer.PROCESSED_DATASET_SAVE_PATH + os.sep + f"validation_dataset_version_{self.version}.csv", index=False
            )
            self.test_dataframe is not None and self.test_dataframe.to_csv(
                Trainer.PROCESSED_DATASET_SAVE_PATH + os.sep + f"test_dataset_version_{self.version}.csv", index=False
            )

        return X_train, X_val, y_train, y_val

    def evaluate_model(self, X_val, y_val):
        """
        Evaluates the model using validation data and calculates different metrics.

        Args:
            X_val (DataFrame or array-like): Validation features.
            y_val (DataFrame or array-like): Actual target values for the validation set.

        Returns:
            dict: A dictionary containing evaluation metrics such as MSE, MAE, R2, and optionally, thresholded versions of these metrics.
        """
        y_pred = self.model.predict(X_val)

        mse = mean_squared_error(y_val, y_pred)
        mae = mean_absolute_error(y_val, y_pred)
        r2 = r2_score(y_val, y_pred)

        results = {"MSE": mse, "MAE": mae, "R2": r2}

        if self.deflection != 0:
            y_val_np = np.array(y_val)
            y_pred_np = np.array(y_pred)

            absolute_errors = np.abs(y_val_np - y_pred_np)

            capped_errors = np.minimum(absolute_errors, self.deflection)

            thresholded_mae = np.mean(capped_errors)
            thresholded_mse = np.mean(capped_errors**2)

            total_variance = np.sum((y_val_np - np.mean(y_val_np)) ** 2)

            thresholded_ss_residual = np.sum((capped_errors) ** 2)

            thresholded_r2 = 1 - (thresholded_ss_residual / total_variance)

            results[f"Thresholded MAE (±{self.deflection})"] = thresholded_mae
            results[f"Thresholded MSE (±{self.deflection})"] = thresholded_mse
            results[f"Thresholded R2 (±{self.deflection})"] = thresholded_r2

        for metric, value in results.items():
            self.logger.info(f"{metric}: {value:.4f}")

        self.registry_meta_data["evaluation_metrics"] = json.dumps(results)

        return results

    def save_model(self):
        """
        Saves the trained model and its configuration to the specified path. Also, registers the model if a supported registry is configured.

        Raises:
            NotImplementedError: If the model registry is not supported.
        """
        if self.model_save_path is not None:
            save_path = os.path.join(Trainer.MODEL_SAVE_PATH, self.experiment_name, os.path.dirname(self.model_save_path))
            os.makedirs(save_path, exist_ok=True)

            if self.model is not None:
                saved_model_abspath = os.path.join(save_path, self.model_save_path)
                saved_train_config_path = os.path.join(save_path, f"{self.experiment_name}_train_config.yml")

                self.registry_meta_data["file_path"] = saved_model_abspath

                with open(saved_train_config_path, "w") as json_file:
                    yaml.dump(self.train_config, json_file, indent=Trainer.YAML_PRETTY_PRINT)

                joblib.dump(self.model, saved_model_abspath)
                self.logger.info(f"Model saved to {saved_model_abspath}.")
                self.logger.info(f"Train config saved to {saved_train_config_path}")

                if self.registry_name.lower() not in Trainer.SUPPORTED_REGISTRY_LIST:
                    raise NotImplementedError("Only ado-flow supported. In future wandb, mlflow will be added.")

                self.check_registry_status() == 200 and self.add_model_to_registry()

            else:
                self.logger.warning("No model has been trained yet to save.")

    def save_callback(func):
        """
        Decorator to save the model after the execution of the wrapped function.

        Args:
            func (callable): The function to be wrapped.

        Returns:
            callable: The wrapped function with additional functionality to save the model.
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Execute the original run method
            result = func(self, *args, **kwargs)

            # Callback to save the model after the run method execution
            self.save_model()

            return result

        return wrapper

    def check_registry_status(self):
        """
        Checks the status of the model registry to ensure it is available.

        Returns:
            int: HTTP status code of the registry status request.
        """
        try:
            response = requests.get(os.path.join(self.registry_url, "status"))  # noqa
            self.logger.registry(f"Status response for ado-flow: {response.json()}")
            return response.status_code
        except Exception as e:
            self.logger.registry_error(f"Could not get status exception {e} occured. Response: {response}")
            return -1

    def add_model_to_registry(self):
        """
        Adds the trained model to the model registry.
        """
        try:
            model_add_request = self.registry_meta_data  # noqa
            response = requests.post(os.path.join(self.registry_url, "upload_model"), json=model_add_request)
            if response == 200:
                self.logger.registry("Model successfully uploaded to registry.")
        except Exception as e:
            self.logger.registry_error(f"Could not upload model exception {e} occured. Response: {response.json()}")

    @abstractmethod
    def run(self):
        """
        Abstract method to define the steps to run the experiment.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def train(self, X_train, y_train):
        """
        Abstract method to define the training process of the model.

        Args:
            X_train (DataFrame or array-like): Training features.
            y_train (DataFrame or array-like): Training target values.

        Must be implemented by subclasses.
        """
        pass


class LinearRegressionTrainer(Trainer):
    def train(self, X_train, y_train):
        self.model = LinearRegression(**self.hyperparameters)
        self.model.fit(X_train, y_train)
        self.logger.info("Model training complete.")

    def run(self):
        X_train, X_val, y_train, y_val = self.prepare_data()
        self.train(X_train, y_train)
        evaluation_results = self.evaluate_model(X_val, y_val)

        return evaluation_results

    run = Trainer.save_callback(run)  # noqa


class XGBoostRegressionTrainer(Trainer):
    def train(self, X_train, y_train):
        self.model = XGBRegressor(**self.hyperparameters)

        self.model.fit(X_train, y_train)
        self.logger.info("XGBoost model training complete.")

    def run(self):
        X_train, X_val, y_train, y_val = self.prepare_data()

        self.train(X_train, y_train)

        evaluation_results = self.evaluate_model(X_val, y_val)

        return evaluation_results

    run = Trainer.save_callback(run)  # noqa


def load_config(file_path):
    with open(file_path) as file:
        data = yaml.safe_load(file)
    return data


# python -m app.trainer.trainer --config app/trainer/configs/linear_regression_train_config.yml
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a model using the specified configuration file.")

    parser.add_argument("--config", type=str, required=True, help="Path to the training configuration YAML file.")

    args = parser.parse_args()
    config_path = args.config

    trainer_logger = Logger(log_file="logs" + os.sep + "trainer_logger.log", debug_mode=False)

    train_config = load_config(file_path=config_path)
    trainer_config = train_config.get("train_config", {})
    model_trainer = trainer_config.get("model_trainer__eval__", None)

    try:
        experiment_name = generate_experiment_name()
        trainer = eval(model_trainer)(train_config=train_config, logger=trainer_logger)
        results = trainer.run()
    except Exception as e:
        print(f"Trainer app has caught an unexpected exception {e}. Traceback: {traceback.format_exc()}")
        trainer_logger.logger.critical(f"Trainer app has caught an unexpected exception {e}. Traceback: {traceback.format_exc()}")
