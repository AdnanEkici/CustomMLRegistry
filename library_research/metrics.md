## Evaluation Metrics for Regression Problems: MAE, MSE, R²

In regression analysis, several evaluation metrics are used to measure the performance of a model. The most common metrics include **Mean Absolute Error (MAE)**, **Mean Squared Error (MSE)**, and **R² (R-squared)**. Each metric provides different insights into the model's accuracy, variability, and error.

### 1. Mean Absolute Error (MAE)

**Mean Absolute Error (MAE)** measures the average magnitude of the errors in a set of predictions, without considering their direction. It is the average of the absolute differences between the predicted and actual values.

- **Formula**:
  \[
  \text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|
  \]
  - **n**: Number of data points.
  - **yᵢ**: Actual value.
  - **ŷᵢ**: Predicted value.

- **Characteristics**:
  - **Scale-dependent**: MAE is in the same unit as the target variable.
  - **Interpretability**: Easy to interpret; represents the average error.

- **When to Use MAE**:
  - When all errors are equally important.
  - When outliers are not significant, as MAE does not square the errors, it is less sensitive to outliers compared to MSE.

### 2. Mean Squared Error (MSE)

**Mean Squared Error (MSE)** measures the average of the squares of the errors—that is, the average squared difference between the estimated values and the actual value.

- **Formula**:
  \[
  \text{MSE} = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2
  \]
  - **n**: Number of data points.
  - **yᵢ**: Actual value.
  - **ŷᵢ**: Predicted value.

- **Characteristics**:
  - **Sensitive to Outliers**: Because the errors are squared, larger errors have a disproportionately large effect on MSE, making it more sensitive to outliers.
  - **Commonly Used**: It is widely used in machine learning due to its desirable mathematical properties.

- **When to Use MSE**:
  - When larger errors are particularly undesirable and need to be penalized more heavily.
  - When the goal is to minimize large deviations in prediction errors.

### 3. R-squared (R²)

**R-squared (R²)**, also known as the **coefficient of determination**, indicates how well the regression predictions approximate the real data points. It provides the proportion of the variance in the dependent variable that is predictable from the independent variables.

- **Formula**:
  \[
  R^2 = 1 - \frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y})^2}
  \]
  - **n**: Number of data points.
  - **yᵢ**: Actual value.
  - **ŷᵢ**: Predicted value.
  - **\bar{y}**: Mean of the actual values.

- **Characteristics**:
  - **Range**: R² ranges from 0 to 1. A value closer to 1 indicates that the model explains most of the variance in the data, while a value closer to 0 indicates that it explains very little.
  - **Interpretability**: Provides a goodness-of-fit measure; higher values are better.

- **When to Use R²**:
  - When you want to understand the proportion of variance explained by the model.
  - For models where you want to evaluate overall goodness-of-fit rather than specific prediction errors.

### Comparison Table

| Metric          | **Formula**                                        | **Characteristics**                                           | **When to Use**                                                                  |
|-----------------|----------------------------------------------------|---------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **MAE**         | \(\text{MAE} = \frac{1}{n} \sum_{i=1}^{n} |y_i - \hat{y}_i|\)           | Average absolute error; less sensitive to outliers            | When all errors are equally important and interpretability is crucial             |
| **MSE**         | \(\text{MSE} = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2\) | Average squared error; more sensitive to outliers              | When larger errors need to be penalized more heavily; commonly used in regression |
| **R² (R-squared)** | \(R^2 = 1 - \frac{\sum_{i=1}^{n} (y_i - \hat{y}_i)^2}{\sum_{i=1}^{n} (y_i - \bar{y})^2}\) | Proportion of variance explained by the model; goodness-of-fit | When evaluating the overall fit of the regression model                           |

### Conclusion

- **MAE**, **MSE**, and **R²** are essential metrics for evaluating regression models. 
- **MAE** provides a straightforward measure of prediction error, while **MSE** is more sensitive to large errors, making it useful for penalizing significant deviations. **R²** helps assess the overall goodness-of-fit of a model.
- The choice of metric depends on the specific problem, the importance of outliers, and the need for interpretability.
