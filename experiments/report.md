

Linear Regression:

Trained with raw dataset results: '{"MSE": 253352.02897039198, "MAE": 385.4219608907223, "R2": 0.027390268276741736}'
Trained with feature engineered rfm dataset results:  {"MSE": 183388.92020159023, "MAE": 330.36071476714864, "R2": 0.23949105827410133}

XGBOOST Regression:

Trained with raw dataset results: '{"MSE": 273011.01558474114, "MAE": 406.5764102444119, "R2": -0.06493189367524188}'
Trained with feature engineered rfm dataset results:  '{"MSE": 205058.2999914094, "MAE": 343.9823089371934, "R2": 0.12065759217040872}'


The Linear Regression model trained with the feature-engineered RFM dataset is better because it has the lowest MSE (183,388), MAE (330.36), and the highest R² (0.239) among all models. This indicates better accuracy and a stronger fit compared to the others.

Feature engineering significantly improves both Linear Regression and XGBoost models, but Linear Regression benefits more from it, leading to better performance overall.
