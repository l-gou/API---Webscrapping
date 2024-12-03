import os
import json
import logging
import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter()

# Define a Pydantic model for the input data (features)
class IrisFeatures(BaseModel):
    SepalLengthCm: float
    SepalWidthCm: float
    PetalLengthCm: float
    PetalWidthCm: float


# Load the trained model from the file
def load_trained_model(model_name: str):
    model_path = os.path.join("TP2and3/services/epf-flower-data-science/src", "models", f"{model_name}.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file '{model_name}.joblib' not found at {model_path}")
    return joblib.load(model_path)


@router.post("/predict", name="Make Predictions with Trained Model")
def predict(model_name: str, features: IrisFeatures):
    try:
        # Load the trained model
        model = load_trained_model(model_name)

        # Prepare the feature data for prediction
        input_data = pd.DataFrame([features.dict()])

        # Make predictions using the trained model
        predictions = model.predict(input_data)

        # Return the predictions as a JSON response
        return JSONResponse(content={
            "model_name": model_name,
            "predictions": predictions.tolist()  # Convert the predictions to a list for JSON compatibility
        })

    except FileNotFoundError as e:
        logging.error(f"Model not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to make prediction: {e}")
