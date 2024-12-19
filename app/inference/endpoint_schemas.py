from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class PredictRequest(BaseModel):
    customer_id: int = Field(..., example=1, description="Unique identifier for the customer")
    age: int = Field(..., example=40, description="Age of the customer")
    gender: str = Field(..., example="Female", description="Gender of the customer")
    annual_income: float = Field(..., example=119228.0, description="Annual income of the customer in USD")
    purchase_amount: float = Field(..., example=986.86, description="Total amount of the last purchase made")
    purchase_date: str = Field(..., example="2023-11-22T19:16:58+03:00", description="Date and time of the last purchase")

    class Config:
        schema_extra = {
            "example": {
                "customer_id": 1,
                "age": 40,
                "gender": "Female",
                "annual_income": 119228,
                "purchase_amount": 986.86,
                "purchase_date": "2023-11-22T19:16:58+03:00",
            }
        }


class PredictResponse(BaseModel):
    next_month_purchase_amount: float = Field(..., example=1050.25, description="Predicted amount of purchases for the next month")
    message: str = Field(..., example="Prediction successful", description="Message providing additional details about the prediction result")
    inference_time: float = Field(..., example=0.123, description="Time taken to run the inference in seconds")
    is_valid_prediction: bool = Field(..., example=True, description="Flag indicating whether the prediction is considered valid")

    class Config:
        schema_extra = {
            "example": {
                "next_month_purchase_amount": 1050.25,
                "message": "Prediction successful",
                "inference_time": 0.123,
                "is_valid_prediction": True,
            }
        }
