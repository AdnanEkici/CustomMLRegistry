from __future__ import annotations
import os
from app.inference.engine import MlInferenceEngine
from marshmallow import ValidationError
from fastapi import FastAPI, HTTPException

import warnings

warnings.filterwarnings("ignore")
from app.inference.endpoint_schemas import PredictRequest  # noreorder # noqa
from app.inference.endpoint_schemas import PredictResponse  # noreorder # noqa
from app.inference.input_schema import ModelInputSchema  # noreorder # noqa
from app.logger.logger import ColorLogger as Logger  # noreorder # noqa


app = FastAPI(title="ML Inference API")
# uvicorn app.inference.endpoint:app --host 0.0.0.0 --port 2000 --workers 4
config_path = "app/inference/configs/inference_config.yml"  # HARDCODED


inference_server_logger = Logger(log_file="logs" + os.sep + "inference_engine_logger.log", debug_mode=False)
inference_engine = MlInferenceEngine(inference_config_path=config_path, logger=inference_server_logger)


@app.post("/predict")
async def predict_endpoint(request: PredictRequest):
    try:
        data = request.dict()
        validated_data = ModelInputSchema().load(data)
        predicted_value, message, inference_time, is_valid_prediction = inference_engine(validated_data)

        return PredictResponse(
            next_month_purchase_amount=predicted_value, message=message, inference_time=inference_time, is_valid_prediction=is_valid_prediction
        )

    except ValidationError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
