from __future__ import annotations

import argparse
import ast
import os
import time
from datetime import datetime
from pathlib import Path

import inflect
import joblib
import numpy as np
import polars as pl
import requests
import yaml


from app.inference.input_schema import ModelInputSchema  # noreorder # noqa
from app.logger.logger import ColorLogger as Logger  # noreorder # noqa


class MlInferenceEngine:
    def __init__(self, inference_config_path, logger) -> None:
        inference_config = load_config(file_path=inference_config_path)
        self.database_path = inference_config["database"]
        self.model_config = inference_config["model"]

        # Model Config Parsing
        self.model_name = self.model_config["name"]
        self.model_version = self.model_config["version"]
        self.model_path = self.model_config["path"]

        # Registry config parsint
        self.registry_config = inference_config["registry"]
        self.registry_name = self.registry_config["name"]
        self.registry_url = self.registry_config["url"]

        self.logger = logger

        self.features = None
        self.model = None

        self.customer_database = pl.scan_csv(self.database_path)  # Let us assume our database is provided csv.
        self.customer_database = self.customer_database.drop("next_month_purchase_amount")
        self.customer_database = self.customer_database.drop_nulls()

        average_values_lazy = self.customer_database.lazy().select(
            [
                pl.col("annual_income").mean().alias("average_annual_income"),
                pl.col("age").mean().cast(pl.Int64).alias("average_age"),  # Casting age to integer
            ]
        )

        # Collect the lazy frame to get a DataFrame
        average_values = average_values_lazy.collect().to_dict(as_series=False)
        self.imputation_income = average_values["average_annual_income"]
        self.imputation_age = average_values["average_age"]

        self.input_scheme = ModelInputSchema()
        self.inflect_engine = inflect.engine()
        self.__fetch_model()

    def __call__(self, raw_input):
        start_time = time.perf_counter()
        predicted_next_month_purchase_amount = 0
        processed_input, is_valid_prediction, msg = self.__preprocess_data(raw_input)
        if is_valid_prediction:
            processed_input = np.array([[processed_input[feature] for feature in self.features]])
            predicted_next_month_purchase_amount = self.model.predict(processed_input)
        end_time = time.perf_counter()

        inference_time = (end_time - start_time) * 1000
        self.logger.info(f"Elapsed time: {inference_time:.3f} ms")

        return predicted_next_month_purchase_amount, msg, inference_time, is_valid_prediction

    def __preprocess_data(self, raw_input: dict):
        validated_data = self.input_scheme.load(raw_input)  # Validate and deserialize

        customer_id = validated_data["customer_id"]
        age = validated_data["age"]
        gender = validated_data["gender"]
        annual_income = validated_data["annual_income"]
        purchase_amount = validated_data["purchase_amount"]
        purchase_date = validated_data["purchase_date"]

        age = self.imputation_age if age == 0 else age
        annual_income = self.imputation_income if annual_income == 0 else annual_income

        customer_block_as_dataframe = self.customer_database.filter(pl.col("customer_id") == customer_id).collect().lazy()
        customer_block_as_dataframe = customer_block_as_dataframe.with_columns(pl.lit(0).alias("recent"))

        customer_count = self.__get_customer_count(customer_id=customer_id, filtered_polars_dataframe=customer_block_as_dataframe)
        msg = ""
        is_valid_data = True
        if customer_count > 0:  #  Old customer has record
            squashed_dataframe = self.__squash_rows(polars_dataframe=customer_block_as_dataframe)
            frequency = squashed_dataframe.height
            squashed_dataframe = self.__add_customer(age, annual_income, gender, purchase_date, purchase_amount, squashed_dataframe)
            one_hot_encoded_df = self.__one_hot_encode(squashed_dataframe)
            processed_input = self.__calculate_rfm(one_hot_encoded_df)

            msg = f"Old customer with customer id {customer_id} detected. This customers {self.inflect_engine.ordinal(int(self.__get_customer_count(customer_id=customer_id, filtered_polars_dataframe=customer_block_as_dataframe)))} purchase."

            processed_input = {
                "age": age,
                "gender_Female": processed_input["gender_Female"][0],
                "Recency": processed_input["Recency"][0],
                "Frequency": frequency,
                "Monetary": processed_input["Monetary"][0],
                "annual_income": annual_income,
                "purchase_amount": purchase_amount,
            }
        else:
            processed_input = None
            msg = f"New customer with customer id {customer_id} detected. Not predicting."
            is_valid_data = False

        self.customer_database = self.customer_database.collect()
        new_rows = [raw_input]
        new_df = pl.DataFrame(new_rows)
        self.customer_database = pl.concat([self.customer_database, new_df])
        self.customer_database = self.customer_database.lazy()  # back to lazy

        return processed_input, is_valid_data, msg

    def __fetch_model(self):
        download = False
        if not os.path.exists(self.model_path):
            download = True
            self.logger.warning("Could not found model in path downloading !")

        if self.__check_registry_status() == 200:
            response = self.__fetch_model_wrapper(download=download)
            self.features = ast.literal_eval(response["model_metadata"]["features"])

            model_basepath = os.path.basename(self.model_path)
            model_prefix = os.path.basename(self.model_path).split(".")[1]
            downloaded_model = f"model__{self.model_name}__{self.model_version}.{model_prefix}"

            if Path(model_basepath).suffix or model_basepath == "":
                model_basepath = "Downloads"

            model_path = os.path.join(model_basepath, downloaded_model)
            self.model = joblib.load(model_path)
            self.logger.info(f"Model features from response: {self.features}")
        else:
            self.logger.registry_error("Could not get connection from regitry cant fetch data ! Attempting to fill features from config !")
            self.features = self.model_config["features"]
            self.model = joblib.load(self.model_path)

    def __calculate_rfm(self, polars_dataframe):
        polars_dataframe = polars_dataframe.with_columns(pl.col("purchase_month_year").str.strptime(pl.Datetime, format="%Y-%m"))

        max_date = polars_dataframe["purchase_month_year"].max()

        def month_diff_expr(date_col, max_date):
            return (pl.lit(max_date).dt.year() - date_col.dt.year()) * 12 + (pl.lit(max_date).dt.month() - date_col.dt.month())

        # Calculate Recency (in months), Frequency, and Monetary
        df_rfm = polars_dataframe.group_by(["recent", "gender_Female"]).agg(
            [  #  Could be more dynamic
                month_diff_expr(pl.col("purchase_month_year"), max_date).min().alias("Recency"),
                pl.count("purchase_month_year").alias("Frequency"),
                pl.sum("total_purchase_amount").alias("Monetary"),
            ]
        )

        processed_input = df_rfm.filter(pl.col("recent") == 1)
        processed_input = processed_input.to_dict(as_series=False)

        return processed_input

    def __one_hot_encode(self, polars_dataframe):
        return polars_dataframe.with_columns(pl.col("gender").cast(pl.Categorical)).to_dummies(  # Ensure 'gender' is treated as a categorical column
            columns=["gender"]
        )

    def __get_customer_count(self, customer_id, filtered_polars_dataframe):
        filtered_df = filtered_polars_dataframe.filter(pl.col("customer_id") == customer_id)
        count_df = filtered_df.select([pl.count().alias("row_count")]).collect()
        customer_count = count_df["row_count"][0]
        return customer_count

    def __add_customer(self, age, annual_income, gender, purchase_date, purchase_amount, polar_dataframe):
        dt = datetime.fromisoformat(str(purchase_date))
        year_month = dt.strftime("%Y-%m")
        new_entry = pl.DataFrame(
            [
                {
                    "age": age,
                    "annual_income": annual_income,
                    "purchase_month_year": str(year_month),
                    "recent": 1,
                    "gender": gender,
                    "total_purchase_amount": float(purchase_amount),
                }
            ]
        )
        return polar_dataframe.vstack(new_entry)

    def __squash_rows(self, polars_dataframe):
        customer_block_as_dataframe = polars_dataframe.with_columns(
            [
                pl.col("purchase_date")
                .str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%z")  # Convert to Datetime
                .dt.strftime("%Y-%m")  # Extract 'YYYY-MM'
                .alias("purchase_month_year")  # Add as a new column
            ]
        ).lazy()
        customer_block_as_dataframe = (
            customer_block_as_dataframe.group_by(["age", "annual_income", "purchase_month_year", "recent", "gender"])
            .agg([pl.col("purchase_amount").sum().alias("total_purchase_amount")])
            .collect()
        )
        customer_block_as_dataframe = customer_block_as_dataframe.with_columns(pl.col("recent").cast(pl.Int64))
        return customer_block_as_dataframe

    def __check_registry_status(self):  # DUPLICATE FUNCTION !!! # TODO TRY to create a utils class.
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
            self.logger.registry_error(f"Could not get status exception {e} occured.")
            return -1

    def __fetch_model_wrapper(self, download: bool = False):
        route = "fetch_and_download_model" if download else "fetch_model"
        try:
            model_add_request = {"name": self.model_name, "version": self.model_version, "download_path": os.path.dirname(self.model_path)}  # noqa
            response = requests.get(os.path.join(self.registry_url, route), json=model_add_request, verify=False)
            if response.status_code == 200:
                self.logger.registry(f"Model successfully fetched. Response: {response.json()}")

            return response.json()
        except Exception as e:
            self.logger.registry_error(f"Could not upload model exception {e} occured. Response: {response}")
        return False


def load_config(file_path):
    with open(file_path) as file:
        data = yaml.safe_load(file)
    return data


# python -m app.inference.engine --config .\app\inference\configs\inference_config.yml
if __name__ == "__main__":
    raw_input = {
        "customer_id": 1,
        "age": 40,
        "gender": "Female",
        "annual_income": 119228,
        "purchase_amount": 986.86,
        "purchase_date": "2023-11-22T19:16:58+03:00",
    }

    parser = argparse.ArgumentParser(description="Start inference engine for testing.")  # TODO: FastAPI could be better researh !

    parser.add_argument("--config", type=str, required=True, help="Path to the inference server configuration YAML file.")

    args = parser.parse_args()
    config_path = args.config

    inference_logger = Logger(log_file="logs" + os.sep + "inference_engine_logger.log", debug_mode=False)

    engine = MlInferenceEngine(inference_config_path=config_path, logger=inference_logger)

    inference_logger.info(f"Predicted Next Month Purchase Amount: {engine(raw_input)}")
