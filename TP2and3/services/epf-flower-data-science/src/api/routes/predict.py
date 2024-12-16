import os
import json
import logging
import joblib
import pandas as pd
from typing import Dict, Any
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
def load_trained_model(model_name: str) -> Any:
    """
    Load a trained model from the file system.

    Parameters:
        model_name (str): The name of the trained model to load.

    Returns:
        Any: The trained model instance.

    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    model_path = os.path.join("TP2and3/services/epf-flower-data-science/src", "models", f"{model_name}.joblib")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file '{model_name}.joblib' not found at {model_path}")
    return joblib.load(model_path)


@router.post("/predict", name="Make Predictions with Trained Model")
def predict(model_name: str, features: IrisFeatures) -> JSONResponse:
    """
    Make predictions using a trained model and provided input features.

    Endpoint:
        POST /predict

    Parameters:
        model_name (str): The name of the trained model to use for predictions.
        features (IrisFeatures): A Pydantic model containing the input features for prediction.

    Returns:
        JSONResponse: A JSON response containing the model name and predictions.

    Raises:
        HTTPException: If the model file is not found or if an error occurs during prediction.
    """
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
