from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import chi2_contingency


class DataframeAnalyzer:
    def __init__(
        self,
        dataframe,
        numerical_columns: list | None = None,
        categorical_columns: list | None = None,
        target_column: str = "next_month_purchase_amount",
    ):
        self.dataframe = dataframe
        self.dataframe_target_excluded = dataframe.drop(columns=[target_column])

        self.numerical_columns = ["age", "annual_income", "purchase_amount"] if numerical_columns is None else numerical_columns.copy()
        self.categorical_columns = ["gender"] if categorical_columns is None else categorical_columns.copy()

        self.numerical_dataframe = self.dataframe[self.numerical_columns]

        self.target_column = target_column

        self.feature_columns = self.numerical_columns + self.categorical_columns

        self.__initialize_helper_classes

    @property
    def __initialize_helper_classes(self):
        self.Statics = self.Statics(self)
        self.Plotter = self.Plotter(self)
        self.Correlation = self.Correlation(self)
        self.ConsistincyChecker = self.ConsistincyChecker(self)
        self.FeatureEngineer = self.FeatureEngineer(self)
        return

    @property
    def get_row_count(self):
        row_count = len(self.dataframe)
        print(f"Total number of rows: {row_count}")
        return row_count

    class Statics:
        def __init__(self, parent):
            self.parent = parent

        @property
        def summary(self):
            return self.parent.dataframe.describe()

        @property
        def get_unique_customer_count(self):
            num_customers = self.parent.dataframe["customer_id"].nunique()
            print(f"Number of unique customer: {num_customers}")
            return num_customers

        @property
        def get_unvalid_data_rows(self):
            rows_with_nan = self.parent.dataframe_target_excluded.isnull().any(axis=1).sum()
            rows_with_inf = self.parent.numerical_dataframe.apply(lambda x: np.isinf(x)).any(axis=1).sum()
            rows_with_invalid = self.parent.numerical_dataframe.apply(lambda x: x < 0).any(axis=1).sum()

            print(f"Number of rows affected by NaN values: {rows_with_nan}")
            print(f"Number of rows affected by Inf values: {rows_with_inf}")
            print(f"Number of rows affected by Invalid values: {rows_with_invalid}")

            return {"NaN": rows_with_nan, "Inf": rows_with_inf, "Invalid": rows_with_invalid}

        @property
        def get_unvalid_data_columns(self):
            nan_counts = self.parent.dataframe.isnull().sum()
            inf_counts = self.parent.numerical_dataframe.apply(lambda x: np.isinf(x).sum())
            negative_counts = self.parent.numerical_dataframe.apply(lambda x: (x < 0).sum())

            print(f"\nCount of NaN values in each column:\n{nan_counts}\n")
            print(f"Count of Inf values in each numerical column:\n{inf_counts}\n")
            print(f"Count of Negative values in each numerical column:\n{negative_counts}")

            return {"NaN": nan_counts, "Inf": inf_counts, "Negative": negative_counts}

        @property
        def get_duplicate_row_count(self):
            duplicate_count = self.parent.dataframe.duplicated().sum()
            print(f"Duplicate row count: {duplicate_count}")
            return duplicate_count

        @property
        def get_all_statistics(self):
            self.get_unique_customer_count
            self.get_unvalid_data_rows
            self.get_unvalid_data_columns
            self.get_duplicate_row_count
            return

    class Plotter:
        def __init__(self, parent):
            self.parent = parent

        def histograms(self):
            for feature in self.parent.numerical_columns + self.parent.categorical_columns:
                plt.figure(figsize=(10, 6))

                if feature in self.parent.numerical_columns:
                    # Plot Histogram for Numerical Features
                    sns.histplot(self.parent.dataframe[feature], kde=False, bins=30)
                    plt.title(f"Histogram of {feature}")
                    plt.xlabel(feature)
                    plt.ylabel("Frequency")

                elif feature in self.parent.categorical_columns:
                    # Plot Bar Plot for Categorical Features
                    sns.countplot(x=self.parent.dataframe[feature])
                    plt.title(f"Bar Plot of {feature}")
                    plt.xlabel(feature)
                    plt.ylabel("Count")

                plt.show()

        def pairwise_scatter(self):
            if len(self.parent.numerical_columns) > 1:  # Ensure there is more than one numerical feature for pairplot
                sns.pairplot(self.parent.dataframe[self.parent.numerical_columns])
                plt.suptitle("Pairwise Scatter Plots of Numeric Features", y=1.02)
                plt.show()
            else:
                print("There is only one numerical feature can not plot pairwise.")

        def box_plots(self):
            for feature in self.parent.numerical_columns:
                plt.figure(figsize=(10, 6))
                sns.boxplot(x=self.parent.dataframe[feature])
                plt.title(f"Box Plot of {feature}")
                plt.xlabel(feature)
                plt.show()

        def kde_plots(self):
            for feature in self.parent.numerical_columns:
                plt.figure(figsize=(10, 6))
                sns.kdeplot(self.parent.dataframe[feature], shade=True)
                plt.title(f"Density Plot (KDE) of {feature}")
                plt.xlabel(feature)
                plt.ylabel("Density")
                plt.show()

        def bar_plots(self):
            """
            Plots bar plots for each categorical feature.
            """
            for feature in self.parent.categorical_columns:
                plt.figure(figsize=(10, 6))
                sns.countplot(x=self.parent.dataframe[feature])
                plt.title(f"Bar Plot of {feature}")
                plt.xlabel(feature)
                plt.ylabel("Count")
                plt.show()

        def numerical_categorical_relationships(self):
            for num_feature in self.parent.numerical_columns:
                for cat_feature in self.parent.categorical_columns:
                    plt.figure(figsize=(10, 6))
                    sns.boxplot(x=self.parent.dataframe[cat_feature], y=self.parent.dataframe[num_feature])
                    plt.title(f"Box Plot of {num_feature} by {cat_feature}")
                    plt.xlabel(cat_feature)
                    plt.ylabel(num_feature)
                    plt.show()

        def violin_plots(self):
            for categorical_feature in self.parent.categorical_columns:
                for numerical_feature in self.parent.numerical_columns:
                    plt.figure(figsize=(10, 6))
                    sns.violinplot(x=self.parent.dataframe[categorical_feature], y=self.parent.dataframe[numerical_feature])
                    plt.title(f"Violin Plot of {numerical_feature} by {categorical_feature}")
                    plt.xlabel(categorical_feature)
                    plt.ylabel(numerical_feature)
                    plt.show()

        def plot_all(self):
            self.histograms()
            self.pairwise_scatter()
            self.box_plots()
            self.kde_plots()
            self.bar_plots()
            self.numerical_categorical_relationships()
            self.violin_plots()

    class Correlation:
        def __init__(self, parent):
            self.parent = parent

        def __cramers_v(confusion_matrix):
            chi2 = chi2_contingency(confusion_matrix)[0]
            n = confusion_matrix.sum().sum()
            r, k = confusion_matrix.shape
            return np.sqrt(chi2 / (n * (min(r, k) - 1)))

        def __correlation_ratio(self, categories, values):
            categories = categories.astype("category")
            category_means = values.groupby(categories).mean()
            overall_mean = values.mean()
            between_group_variance = ((category_means - overall_mean) ** 2).sum() * categories.value_counts()
            total_variance = ((values - overall_mean) ** 2).sum()
            return np.sqrt(between_group_variance.sum() / total_variance)

        def categorical_correlation_matrix(self, plot: bool = False, categorical_columns: list | None = None):
            if categorical_columns is None:
                categorical_columns = self.parent.categorical_columns

            if len(categorical_columns) > 1:
                correlation_matrix = pd.DataFrame(index=categorical_columns, columns=categorical_columns)

                for col1 in categorical_columns:
                    for col2 in categorical_columns:
                        if col1 == col2:
                            correlation_matrix.loc[col1, col2] = 1.0
                        else:
                            confusion_matrix = pd.crosstab(self.parent.dataframe[col1], self.parent.dataframe[col2])
                            correlation_matrix.loc[col1, col2] = self.__cramers_v(confusion_matrix)  # noqa

                if plot:
                    correlation_matrix = correlation_matrix.astype(float)
                    plt.figure(figsize=(10, 8))
                    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
                    plt.title("Categorical-Categorical Correlation Matrix (Cramér's V)")
                    plt.show()

                return correlation_matrix
            print("At least 2 features need to calculate corelation matrix.")
            return None

        def numerical_correlation_matrix(self, method="pearson", plot: bool = False, numerical_columns: list | None = None):
            if numerical_columns is None:
                numerical_columns = self.parent.numerical_columns

            if len(numerical_columns) > 1:
                correlation_matrix = self.parent.dataframe[numerical_columns].corr(method=method)

                if plot:
                    plt.figure(figsize=(10, 8))
                    sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
                    plt.title(f"Numerical-Numerical Correlation Matrix ({method.capitalize()})")
                    plt.show()

                return correlation_matrix
            print("At least 2 features need to calculate corelation matrix.")
            return None

        def categorical_numerical_correlation_matrix(self, plot: bool = False):
            correlation_matrix = pd.DataFrame(index=self.parent.categorical_columns, columns=self.parent.numerical_columns)

            for cat_feature in self.parent.categorical_columns:
                for num_feature in self.parent.numerical_columns:
                    correlation_matrix.loc[cat_feature, num_feature] = self.__correlation_ratio(
                        self.parent.dataframe[cat_feature], self.parent.dataframe[num_feature]
                    )

            correlation_matrix = correlation_matrix.astype(float)

            if plot:
                plt.figure(figsize=(10, 8))
                sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
                plt.title("Categorical-Numerical Correlation Matrix (Correlation Ratio η²)")
                plt.show()

            return correlation_matrix

    class ConsistincyChecker:
        def __init__(self, parent):
            self.parent = parent

        def check_constant_column_consistency(self, constant_columns):
            inconsistent_details = {}

            for column in constant_columns:
                inconsistent_data = self.parent.dataframe.groupby("customer_id")[column].apply(lambda x: x.unique())
                inconsistent_customer_ids = inconsistent_data[inconsistent_data.apply(lambda x: len(x) > 1)]

                if not inconsistent_customer_ids.empty:
                    inconsistent_details[column] = inconsistent_customer_ids.to_dict()

            # Print the inconsistencies
            if inconsistent_details:
                print("Inconsistencies found in the following columns for these customer_ids:")
                for column, details in inconsistent_details.items():
                    print(f"\n- {column}:")
                    for customer_id, values in details.items():
                        print(f"  Customer ID {customer_id}: {list(values)}")
            else:
                print("No inconsistencies found in the dataset for the specified columns.")

            return inconsistent_details

        def check_age_consistency(self):
            inconsistent_ages = {}

            for customer_id, group in self.parent.dataframe.groupby("customer_id"):
                sorted_group = group.sort_values("purchase_date")

                if (sorted_group["age"].diff().dropna() < 0).any():
                    inconsistent_ages[customer_id] = sorted_group[["purchase_date", "age"]].values.tolist()

            if inconsistent_ages:
                print("Inconsistencies found in the 'age' column for the following customer_ids:")
                for customer_id, values in inconsistent_ages.items():
                    print(f"\n- Customer ID {customer_id}:")
                    for date, age in values:
                        print(f"  Purchase Date: {date}, Age: {age}")
            else:
                print("No inconsistencies found in the 'age' column.")

            return inconsistent_ages

    class FeatureEngineer:
        def __init__(self, parent):
            self.parent = parent

        def squash_rows_by_customer_month_year(self):
            self.parent.dataframe["purchase_date"] = pd.to_datetime(self.parent.dataframe["purchase_date"])
            self.parent.dataframe["purchase_year"] = self.parent.dataframe["purchase_date"].dt.year
            self.parent.dataframe["purchase_month"] = self.parent.dataframe["purchase_date"].dt.month

            self.parent.dataframe = (
                self.parent.dataframe.groupby(["customer_id", "purchase_year", "purchase_month"])
                .agg(
                    {
                        "age": "first",
                        "gender": "first",
                        "annual_income": "first",
                        "purchase_date": "first",
                        "purchase_amount": "sum",
                        "next_month_purchase_amount": "first",
                    }
                )
                .reset_index()
            )

            return self.parent.dataframe

        def compute_next_month_purchase_amount(self):
            def next_month_year(row):
                if row["purchase_month"] == 12:
                    return row["purchase_year"] + 1, 1
                else:
                    return row["purchase_year"], row["purchase_month"] + 1

            self.parent.dataframe[["next_year", "next_month"]] = self.parent.dataframe.apply(next_month_year, axis=1, result_type="expand")

            merged_df = pd.merge(
                self.parent.dataframe,
                self.parent.dataframe[["customer_id", "purchase_year", "purchase_month", "purchase_amount"]],
                left_on=["customer_id", "next_year", "next_month"],
                right_on=["customer_id", "purchase_year", "purchase_month"],
                how="left",
                suffixes=("", "_next"),
            )

            self.parent.dataframe["next_month_purchase_amount"] = merged_df["purchase_amount_next"]

            for idx, row in self.parent.dataframe[self.parent.dataframe["next_month_purchase_amount"].isna()].iterrows():
                future_purchases = self.parent.dataframe[
                    (self.parent.dataframe["customer_id"] == row["customer_id"])
                    & (
                        (self.parent.dataframe["purchase_year"] > row["purchase_year"])
                        | (
                            (self.parent.dataframe["purchase_year"] == row["purchase_year"])
                            & (self.parent.dataframe["purchase_month"] > row["purchase_month"])
                        )
                    )
                ]

                if not future_purchases.empty:
                    closest_purchase = future_purchases.sort_values(["purchase_year", "purchase_month"]).iloc[0]
                    self.parent.dataframe.at[idx, "next_month_purchase_amount"] = closest_purchase["purchase_amount"]

            self.parent.dataframe.drop(columns=["next_year", "next_month"], inplace=True)
            return self.parent.dataframe

        def drop_invalid_rows(self):
            columns_to_check = [col for col in self.parent.numerical_columns if col in self.parent.dataframe.columns]

            print(f"Initial row count: {self.parent.dataframe.shape[0]}")

            self.parent.dataframe = self.parent.dataframe[~self.parent.dataframe[self.parent.feature_columns].isnull().any(axis=1)]
            print(f"Row count after dropping NaNs: {self.parent.dataframe.shape[0]}")  # Debug

            numerical_columns_to_check = self.parent.dataframe[columns_to_check].select_dtypes(include=[np.number]).columns

            self.parent.dataframe = self.parent.dataframe[~self.parent.dataframe[numerical_columns_to_check].applymap(np.isinf).any(axis=1)]
            print(f"Row count after dropping Infs: {self.parent.dataframe.shape[0]}")  # Debug

            self.parent.dataframe = self.parent.dataframe[~(self.parent.dataframe[numerical_columns_to_check] < 0).any(axis=1)]
            print(f"Row count after dropping negative values: {self.parent.dataframe.shape[0]}")  # Debug

            return self.parent.dataframe

        def one_hot_encode_categorical_data(self):
            categorical_columns = [col for col in self.parent.categorical_columns if col in self.parent.dataframe.columns]
            encoded_df = pd.get_dummies(self.parent.dataframe[categorical_columns], drop_first=False)
            columns_to_add = [col for col in encoded_df.columns if col not in self.parent.dataframe.columns]
            self.parent.dataframe = pd.concat([self.parent.dataframe, encoded_df[columns_to_add]], axis=1)
            return self.parent.dataframe

        def find_outliers_z_score(self, column, threshold=3, drop: bool = True):
            mean = self.parent.dataframe[column].mean()
            std = self.parent.dataframe[column].std()

            z_scores = (self.parent.dataframe[column] - mean) / std

            outliers = self.parent.dataframe[z_scores.abs() > threshold]

            outlier_customer_ids = outliers["customer_id"].unique()
            outlier_row_indices = outliers.index.tolist()

            # print(f"Customer IDs with outliers in column '{column}' based on Z-Score method:")
            print(outlier_customer_ids)
            print(f"Row indices with outliers in column '{column}' based on Z-Score method:")
            print(outlier_row_indices)

            if drop:
                self.parent.dataframe.drop(outlier_row_indices, inplace=True)
                print(f"Dropped {len(outlier_row_indices)} rows with outliers from the DataFrame.")

            return outlier_row_indices, outlier_customer_ids

        def find_outliers_iqr(self, column, drop: bool = False):
            Q1 = self.parent.dataframe[column].quantile(0.25)
            Q3 = self.parent.dataframe[column].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # Identify outliers
            outliers = self.parent.dataframe[(self.parent.dataframe[column] < lower_bound) | (self.parent.dataframe[column] > upper_bound)]

            outlier_customer_ids = outliers["customer_id"].unique()
            outlier_row_indices = outliers.index.tolist()

            # print(f"Customer IDs with outliers in column '{column}' based on IQR method:")
            print(outlier_customer_ids)
            print(f"Row indices with outliers in column '{column}' based on IQR method:")
            print(outlier_row_indices)

            if drop:
                self.parent.dataframe.drop(outlier_row_indices, inplace=True)
                print(f"Dropped {len(outlier_row_indices)} rows with outliers from the DataFrame.")

            return outlier_row_indices, outlier_customer_ids

        def calculate_rfm(self, customer_id_col="customer_id", date_col="purchase_date", amount_col="purchase_amount"):
            # Ensure the 'purchase_date' column is in datetime format
            self.parent.dataframe[date_col] = pd.to_datetime(self.parent.dataframe[date_col])

            # Define a reference date for recency calculation (e.g., the most recent date in the dataset + 1 day)
            reference_date = self.parent.dataframe[date_col].max() + pd.Timedelta(days=1)

            # Calculate Recency: Days since last purchase for each customer
            self.parent.dataframe["Recency"] = self.parent.dataframe.groupby(customer_id_col)[date_col].transform(
                lambda x: (reference_date - x.max()).days
            )

            # Calculate Frequency: Total number of purchases for each customer
            self.parent.dataframe["Frequency"] = self.parent.dataframe.groupby(customer_id_col)[date_col].transform("count")

            # Calculate Monetary: Total amount spent by each customer
            self.parent.dataframe["Monetary"] = self.parent.dataframe.groupby(customer_id_col)[amount_col].transform("sum")

            # Remove duplicate rows caused by groupby transforms
            # self.parent.dataframe = self.parent.dataframe.drop_duplicates(subset=[customer_id_col, 'Recency', 'Frequency', 'Monetary'])

            self.parent.numerical_columns = self.parent.numerical_columns + ["Recency", "Frequency", "Monetary"]

            return self.parent.dataframe

    def print_customers_with_nan_in_column(self, column):
        if column not in self.dataframe.columns:
            print(f"Column '{column}' does not exist in the DataFrame.")
            return

        # Check for NaN values in the specified column
        nan_rows = self.dataframe[self.dataframe[column].isnull()]

        # If there are NaN values, print the 'customer_id's
        if not nan_rows.empty:
            print(f"Customer IDs with NaN in column '{column}':")
            print(nan_rows["customer_id"].unique())
        else:
            print(f"No NaN values found in column '{column}'.")

    def separate_and_save_datasets(self, train_filename="train_dataset.csv", test_filename="test_dataset.csv"):
        if self.target_column not in self.dataframe.columns:
            print(f"Column '{self.target_column}' does not exist in the DataFrame.")
            return

        test_df = self.dataframe[self.dataframe[self.target_column].isnull()]
        train_df = self.dataframe[~self.dataframe[self.target_column].isnull()]

        test_df.to_csv(test_filename, index=False)
        train_df.to_csv(train_filename, index=False)

        print(f"DataFrames have been separated and saved to {train_filename} and {test_filename}.")


if __name__ == "__main__":
    import time

    start_time = time.perf_counter()

    # Avarage 6,2 ms
    dataframe = pd.read_csv("data/customer_purchases.csv")
    dataset_processor = DataframeAnalyzer(dataframe=dataframe)
    dataset_processor.FeatureEngineer.squash_rows_by_customer_month_year()  # noqa
    dataset_processor.FeatureEngineer.compute_next_month_purchase_amount()  # noqa
    dataset_processor.FeatureEngineer.one_hot_encode_categorical_data()  # noqa
    dataset_processor.FeatureEngineer.drop_invalid_rows()  # noqa
    dataset_processor.FeatureEngineer.calculate_rfm()  # noqa
    [
        dataset_processor.FeatureEngineer.find_outliers_iqr(column=column, drop=True)  # noqa
        for column in ["age", "annual_income", "purchase_amount", "Recency", "Frequency", "Monetary"]
    ]

    end_time = time.perf_counter()
    elapsed_time_ms = (end_time - start_time) * 1000
    print(f"Elapsed time: {elapsed_time_ms:.3f} ms")
