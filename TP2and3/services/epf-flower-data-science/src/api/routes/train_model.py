import os
import json
import logging
import joblib
import pandas as pd
from fastapi import APIRouter
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from fastapi.responses import JSONResponse

from src.api.routes import split

router = APIRouter()

# Load model parameters from the JSON file
def load_model_parameters():
    model_params_path = os.path.join("TP2and3/services/epf-flower-data-science/src/config", "model_parameters.json")
    if not os.path.exists(model_params_path):
        raise FileNotFoundError(f"Model parameters file not found at {model_params_path}")
    
    with open(model_params_path, 'r') as f:
        return json.load(f)


# Select the model based on the name and parameters
def get_model(model_name, params):
    if model_name == "RandomForestClassifier":
        return RandomForestClassifier(**params)
    elif model_name == "SVC":
        return SVC(**params)
    elif model_name == "KNeighborsClassifier":
        return KNeighborsClassifier(**params)
    elif model_name == "DecisionTreeClassifier":
        return DecisionTreeClassifier(**params)
    elif model_name == "GaussianNB":
        return GaussianNB(**params)
    else:
        raise ValueError(f"Model '{model_name}' not recognized.")


@router.get("/train-model", name="Train a Classification Model")
def train_model(model_name: str):
    try:
        # Call the split_data function from the split module and get the data
        split_data_response = split.split_data()

        # If the response is a JSONResponse, extract the body content and parse it as JSON
        if isinstance(split_data_response, JSONResponse):
            split_data = split_data_response.body.decode("utf-8")  # Decode the response body
            split_data = json.loads(split_data)  # Convert the string to a Python dictionary
        else:
            split_data = split_data_response  # If it's already a dict, use it directly

        # Check if the response contains the necessary data
        if "train_data" not in split_data or "test_data" not in split_data:
            return {"error": "Split data does not contain the required fields."}

        # Extract the train data
        train_data = split_data["train_data"]
        X_train = pd.DataFrame(train_data["X_train"])
        y_train = pd.Series(train_data["y_train"])

        # Load model parameters
        model_params = load_model_parameters()

        if model_name not in model_params:
            return {"error": f"Model '{model_name}' parameters not found."}

        # Get the parameters for the selected model
        model_params_for_selected = model_params[model_name]

        # Get the model instance
        model = get_model(model_name, model_params_for_selected)

        # Train the model
        model.fit(X_train, y_train)

        # Ensure the directory exists before saving the model
        model_dir = os.path.join("TP2and3/services/epf-flower-data-science/src", "models")
        os.makedirs(model_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Save the trained model to the src/models folder
        model_save_path = os.path.join(model_dir, f"{model_name}.joblib")
        joblib.dump(model, model_save_path)

        return JSONResponse(content={
            "message": f"Model '{model_name}' trained and saved to {model_save_path}",
            "model_path": model_save_path
        })

    except Exception as e:
        logging.error(f"Error training model: {e}")
        return {"error": f"Failed to train model: {e}"}
