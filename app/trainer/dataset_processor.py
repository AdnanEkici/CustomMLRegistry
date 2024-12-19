from __future__ import annotations

import os  # noqa
import warnings  # noreorder # noqa

warnings.simplefilter(action="ignore", category=FutureWarning)  # noreorder # noqa
warnings.simplefilter(action="ignore", category=UserWarning)  # noreorder # noqa
import multiprocessing  # noreorder # noqa

total_cores = multiprocessing.cpu_count()  # noreorder # noqa
half_cores = max(1, total_cores // 2)  # noreorder # noqa
os.environ["POLARS_MAX_THREADS"] = str(total_cores)  # noreorder # noqa

import polars as pl  # noreorder # noqa
from datetime import timedelta  # noqa
from typing import Final  # noqa


class DatasetProcessor:
    MICROSECONDS_PER_DAD: Final = 24 * 60 * 60 * 1000000  # ( 24 Hours 60 Minutes * 60 Second * 1000000 Miscrosecond )

    def __init__(
        self,
        csv_path,
        numerical_columns: list | None = None,
        categorical_columns: list | None = None,
        features: list | None = None,
        target_column: str = "next_month_purchase_amount",
    ) -> None:
        self.dataframe = pl.read_csv(csv_path)
        self.categorical_columns = ["gender"]
        self.numerical_columns = ["age", "annual_income", "purchase_amount"]
        self.target_column = target_column

        self.numerical_columns = ["age", "annual_income", "purchase_amount"] if numerical_columns is None else numerical_columns.copy()
        self.categorical_columns = ["gender"] if categorical_columns is None else categorical_columns.copy()

        self.features = ["age", "annual_income", "purchase_amount", "Recency", "Frequency", "Monetary"] if features is None else features

    def __squash_rows_by_customer_month_year(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        self.dataframe = self.dataframe.with_columns(
            pl.col("purchase_date").str.strptime(pl.Datetime, format="%Y-%m-%dT%H:%M:%S%z").alias("purchase_date")
        )

        self.dataframe = self.dataframe.with_columns(
            [pl.col("purchase_date").dt.year().alias("purchase_year"), pl.col("purchase_date").dt.month().alias("purchase_month")]
        )

        self.dataframe = self.dataframe.group_by(["customer_id", "purchase_year", "purchase_month"]).agg(
            [
                pl.col("age").first().alias("age"),
                pl.col("gender").first().alias("gender"),
                pl.col("annual_income").first().alias("annual_income"),
                pl.col("purchase_date").first().alias("purchase_date"),
                pl.col("purchase_amount").sum().alias("purchase_amount"),
                pl.col("next_month_purchase_amount").first().alias("next_month_purchase_amount"),
            ]
        )

        return self.dataframe

    def __compute_next_month_purchase_amount(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        if self.dataframe["purchase_date"].dtype != pl.Datetime:
            self.dataframe = self.dataframe.with_columns(
                pl.col("purchase_date").str.strptime(pl.Datetime, "%Y-%m-%dT%H:%M:%S%.f%z", strict=False).alias("purchase_date")
            )

        self.dataframe = self.dataframe.with_columns(
            [
                (pl.when(pl.col("purchase_month") == 12).then(pl.col("purchase_year") + 1).otherwise(pl.col("purchase_year"))).alias("next_year"),
                (pl.when(pl.col("purchase_month") == 12).then(1).otherwise(pl.col("purchase_month") + 1)).alias("next_month"),
            ]
        )

        self.dataframe = self.dataframe.with_row_count(name="index")

        next_month_df = self.dataframe.join(
            self.dataframe.select(["customer_id", "purchase_year", "purchase_month", "purchase_amount"]),
            left_on=["customer_id", "next_year", "next_month"],
            right_on=["customer_id", "purchase_year", "purchase_month"],
            how="left",
            suffix="_next",
        )

        self.dataframe = self.dataframe.with_columns(next_month_df["purchase_amount_next"].alias("next_month_purchase_amount"))

        updated_rows = []
        for row in self.dataframe.iter_rows(named=True):
            if row["next_month_purchase_amount"] is None:
                future_purchases = self.dataframe.filter(
                    (pl.col("customer_id") == row["customer_id"])
                    & (
                        (pl.col("purchase_year") > row["purchase_year"])
                        | ((pl.col("purchase_year") == row["purchase_year"]) & (pl.col("purchase_month") > row["purchase_month"]))
                    )
                ).sort(["purchase_year", "purchase_month"])

                if len(future_purchases) > 0:
                    closest_purchase = future_purchases[0]
                    updated_rows.append((row["index"], closest_purchase["purchase_amount"]))

        for index, value in updated_rows:
            self.dataframe[index, "next_month_purchase_amount"] = value

        self.dataframe = self.dataframe.drop(["next_year", "next_month", "index"])
        self.dataframe = self.dataframe.sort("customer_id")
        return self.dataframe

    def __one_hot_encode_categorical_data(self):
        """One-hot encodes the 'gender' column in the DataFrame.

        Returns:
            pl.DataFrame: The DataFrame with one-hot encoded gender columns.
        """
        categorical_columns = [col for col in self.categorical_columns if col in self.dataframe.columns]

        for col in categorical_columns:
            unique_values = self.dataframe[col].unique().to_list()

            for value in unique_values:
                dummy_column = self.dataframe.select((pl.col(col) == value).cast(pl.Int8).alias(f"{col}_{value}"))
                self.dataframe = self.dataframe.hstack(dummy_column)

        self.dataframe = self.dataframe.drop("gender_None")
        return self.dataframe

    def __drop_rows_with_nan(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        for col in self.numerical_columns:
            self.dataframe = self.dataframe.filter(pl.col(col).is_not_null())

        return self.dataframe

    def __find_outliers_iqr(self, column, drop: bool = True):
        """_summary_

        Args:
            column (_type_): _description_
            drop (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        """
        Q1 = self.dataframe.select(pl.col(column).quantile(0.25)).item()
        Q3 = self.dataframe.select(pl.col(column).quantile(0.75)).item()
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = self.dataframe.filter((pl.col(column) < lower_bound) | (pl.col(column) > upper_bound))

        outlier_customer_ids = outliers["customer_id"].unique().to_list()
        outlier_row_indices = outliers["customer_id"].to_list()

        if drop:
            self.dataframe = self.dataframe.filter((pl.col(column) >= lower_bound) & (pl.col(column) <= upper_bound))

        return outlier_row_indices, outlier_customer_ids

    def __calculate_rfm(self, customer_id_col="customer_id", date_col="purchase_date", amount_col="purchase_amount"):
        """Calculate RFM (Recency, Frequency, Monetary) metrics for each customer in the DataFrame.

        Args:
            customer_id_col (str, optional): Column name for customer ID. Defaults to 'customer_id'.
            date_col (str, optional): Column name for purchase date. Defaults to 'purchase_date'.
            amount_col (str, optional): Column name for purchase amount. Defaults to 'purchase_amount'.

        Returns:
            pl.DataFrame: DataFrame with RFM metrics added.
        """
        reference_date = self.dataframe.select(pl.col(date_col).max())[0, 0] + timedelta(days=1)

        rfm_df = self.dataframe.group_by(customer_id_col).agg(
            [
                ((reference_date - pl.col(date_col).max()).cast(pl.Int64) / DatasetProcessor.MICROSECONDS_PER_DAD).alias(
                    "Recency"
                ),  # Convert microseconds to days
                pl.count(date_col).alias("Frequency"),
                pl.sum(amount_col).alias("Monetary"),
            ]
        )

        self.dataframe = self.dataframe.join(rfm_df, on=customer_id_col, how="left")

        return self.dataframe

    def __separate_and_save_datasets(self, train_filename="polar_train_dataset.csv", test_filename="polars_test_dataset.csv", save: bool = False):
        """_summary_

        Args:
            train_filename (str, optional): _description_. Defaults to 'polar_train_dataset.csv'.
            test_filename (str, optional): _description_. Defaults to 'polars_test_dataset.csv'.
            save (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        if self.target_column not in self.dataframe.columns:
            print(f"Column '{self.target_column}' does not exist in the DataFrame.")
            return

        test_df = self.dataframe.filter(pl.col(self.target_column).is_null())
        train_df = self.dataframe.filter(pl.col(self.target_column).is_not_null())
        train_df = self.dataframe.drop_nulls()

        save and test_df.write_csv(test_filename)
        save and train_df.write_csv(train_filename)

        return train_df, test_df

    def process_dataset(self, save: bool = False):
        """_summary_

        Args:
            save (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        self.__squash_rows_by_customer_month_year()
        self.__compute_next_month_purchase_amount()
        self.__one_hot_encode_categorical_data()
        self.__drop_rows_with_nan()
        self.__calculate_rfm()
        [self.__find_outliers_iqr(column=column, drop=True) for column in self.features]
        train_dataset, test_dataset = self.__separate_and_save_datasets(save=save)
        return train_dataset.to_pandas(), test_dataset.to_pandas()


if __name__ == "__main__":
    import time

    # Avarage 1,7 ms
    start_time = time.perf_counter()

    dataset_processor = DatasetProcessor(csv_path="data/customer_purchases.csv")
    dataset_processor.process_dataset(save=True)
    end_time = time.perf_counter()
    elapsed_time_ms = (end_time - start_time) * 1000
    print(f"Elapsed time: {elapsed_time_ms:.3f} ms")
