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
    try:
        # Process data first (scaling) by calling the /process-data endpoint
        iris_response = process.process_data()  # Get the processed (scaled) data

        # Check if the response contains an error
        if isinstance(iris_response, dict) and "error" in iris_response:
            return iris_response  # Return the error if it exists

        # Extract the content from the JSONResponse
        iris_json = iris_response.body.decode("utf-8")  # Decode the response body
        import json
        iris_data = json.loads(iris_json)  # Convert the JSON string into a Python dictionary
        
        # Check if 'data' key exists and extract it
        if 'data' in iris_data:
            iris_data = iris_data['data']  # Extract the nested data

        # Convert the processed data back into a DataFrame
        iris_df = pd.DataFrame(iris_data)

        # Clean column names by stripping any extra spaces
        iris_df.columns = iris_df.columns.str.strip()  # Clean column names

        # Log the columns to check if 'Species' is there
        logging.info(f"Columns in the DataFrame after cleaning: {iris_df.columns.tolist()}")

        # Check if 'Species' exists in the columns after stripping
        if 'Species' not in iris_df.columns:
            return {"error": "Failed to process dataset: 'Species' column not found."}

        # Separate features and target
        X = iris_df.iloc[:, :-1]  # Features (all columns except 'Species')
        y = iris_df['Species']    # Target (the 'Species' column)

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

        # Return the split data as JSON response
        return JSONResponse(content={
            "train_data": train_data,
            "test_data": test_data
        })

    except Exception as e:
        logging.error(f"Error splitting dataset: {e}")
        return {"error": f"Failed to split dataset: {e}"}
