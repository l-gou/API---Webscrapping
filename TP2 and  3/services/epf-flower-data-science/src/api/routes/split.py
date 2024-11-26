import os
import pandas as pd
import logging
from fastapi import APIRouter
from sklearn.model_selection import train_test_split
from fastapi.responses import JSONResponse

from src.api.routes import process

router = APIRouter()


@router.get("/split-data", name="Split Iris Dataset")
def split_data():
    data_dir = "TP2 and  3/services/epf-flower-data-science/src/data"
    iris_path = os.path.join(data_dir, "iris.csv")

    if not os.path.exists(iris_path):
        return {"error": "Dataset not found. Please download the dataset first."}

    try:
        # Process data first (scaling)
        iris_scaled_json = process.process_data()  # Get the processed (scaled) data from the /process-data endpoint

        if isinstance(iris_scaled_json, dict) and "error" in iris_scaled_json:
            # Return the error if the data processing failed
            return iris_scaled_json
        
        # Convert the processed data back into a DataFrame
        iris_df = pd.DataFrame(iris_scaled_json)
        
        # Separate features and target
        X = iris_df.iloc[:, :-1]  # Features (exclude the last column 'species')
        y = iris_df['Species']    # Target (species column)
        
        # Split data into training and testing sets (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Prepare the response data
        train_data = {
            "X_train": X_train.values.tolist(),
            "y_train": y_train.values.tolist()
        }
        test_data = {
            "X_test": X_test.values.tolist(),
            "y_test": y_test.values.tolist()
        }
        
        return JSONResponse(content={
            "train_data": train_data,
            "test_data": test_data
        })
    except Exception as e:
        logging.error(f"Error splitting dataset: {e}")
        return {"error": f"Failed to split dataset: {e}"}