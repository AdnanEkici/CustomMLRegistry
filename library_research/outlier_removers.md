## Outlier Detection Methods: IQR and Z-Score

Outlier detection is a crucial step in data analysis to ensure the quality and accuracy of statistical analyses and machine learning models. Two common methods for detecting outliers are **IQR (Interquartile Range)** and **Z-Score**. Both techniques are useful in different scenarios based on the distribution of data and the nature of the dataset.

### 1. IQR (Interquartile Range) Method

**IQR** is a measure of statistical dispersion and is defined as the difference between the 75th percentile (Q3) and the 25th percentile (Q1) of the data. The IQR method is used to detect outliers by identifying points that fall significantly above or below the range of most of the data.

- **Formula**:
  - **IQR** = Q3 - Q1
  - Outliers are typically defined as data points that fall below **Q1 - 1.5 * IQR** or above **Q3 + 1.5 * IQR**.

- **When to Use IQR**:
  - **Non-Normally Distributed Data**: IQR is robust to non-normal distributions and skewed data. It does not rely on any assumptions about the underlying data distribution.
  - **Data with Skewness or Heavy Tails**: If the data is skewed or has heavy tails, IQR is preferred over Z-score since it is less affected by extreme values.
  - **Non-Parametric Analysis**: When the analysis does not assume a normal distribution, IQR provides a more reliable method for detecting outliers.

- **Why Use IQR**:
  - **Resistant to Outliers**: IQR is based on percentiles and is not affected by extreme values, making it ideal for data that is not normally distributed.
  - **Simple to Compute**: It is straightforward to calculate and interpret, especially for univariate data.


## Z-Score Method for Outlier Detection

**Z-Score** is a statistical measure that describes a data point's relationship to the mean of a group of data points. It is expressed in terms of standard deviations from the mean. The Z-Score method is commonly used to identify outliers in a dataset, especially when the data follows a normal (Gaussian) distribution.

### What is a Z-Score?

- **Definition**: A Z-Score indicates how many standard deviations a data point is from the mean of the dataset. A Z-Score can be positive or negative, indicating whether the data point is above or below the mean.
- **Formula**:
  \[
  \text{Z-Score} = \frac{X - \mu}{\sigma}
  \]
  - **X**: The value of the data point.
  - **μ (mu)**: The mean of the dataset.
  - **σ (sigma)**: The standard deviation of the dataset.
- **Outlier Detection**: Data points with a Z-Score greater than +3 or less than -3 are often considered outliers, although the threshold can vary based on the specific application.

### When to Use Z-Score?

- **Normally Distributed Data**: Z-Score is most effective when the data is normally distributed. It relies on the properties of the normal distribution to identify outliers.
- **Symmetrical Data**: Works well with data that is symmetrical around the mean.
- **Parametric Analysis**: If the analysis is based on parametric methods (which assume normal distribution), Z-Score is an appropriate choice.
- **Large Sample Sizes**: For large datasets that follow a normal distribution, Z-Score provides a precise way of identifying extreme values.

### Why Use Z-Score?

- **Easy Interpretation**: Z-Scores are standardized, making them easy to understand and interpret. A Z-Score of 1 means the data point is 1 standard deviation away from the mean.
- **Widely Used**: Z-Score is a common method for detecting outliers in fields like finance, economics, and quality control.
- **Good for Outlier Identification in Symmetrical Data**: For data that is normally distributed, Z-Score is an effective tool to identify outliers that deviate significantly from the mean.