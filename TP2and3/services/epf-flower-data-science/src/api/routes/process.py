import os
import pandas as pd
import logging
from fastapi import APIRouter
from sklearn.preprocessing import StandardScaler
from fastapi.responses import JSONResponse
from src.api.routes import load  


router = APIRouter()

@router.get("/process-data", name="Process Iris Dataset")
def process_data():
    data_dir = "TP2and3/services/epf-flower-data-science/src/data"
    iris_path = os.path.join(data_dir, "iris.csv")

    if not os.path.exists(iris_path):
        return {"error": "Dataset not found. Please download the dataset first."}

    try:
        # Get the dataset from the /load-iris-dataset endpoint (via load function)
        iris_response = load.load_iris_dataset()  # Call the load function to get the data

        # Check if the response contains an error
        if isinstance(iris_response, dict) and "error" in iris_response:
            return iris_response  # Return the error if it exists
        
        # Extract the actual content from JSONResponse (assuming it returns JSON in the body)
        iris_json = iris_response.body.decode("utf-8")  # Get the response body and decode it
        
        # Convert the string into a dictionary (JSON data)
        import json
        iris_data = json.loads(iris_json)

        # Check if the data is nested under a key like 'data'
        if 'data' in iris_data:
            iris_data = iris_data['data']  # Extract the nested data

        # Convert the processed data back into a DataFrame
        iris_df = pd.DataFrame(iris_data)

        # Log the columns for debugging
        logging.info(f"Columns in the DataFrame: {iris_df.columns.tolist()}")

        # Fix potential issues with column names (strip any whitespace)
        iris_df.columns = iris_df.columns.str.strip()

        # Check if 'Species' column exists (after cleaning the column names)
        if 'Species' not in iris_df.columns:
            return {"error": "Failed to process dataset: 'Species' column not found in the data."}

        # Separate features and target
        y = iris_df['Species']    # Target (species column)
        X = iris_df.drop(iris_df.columns[[0, -1]], axis=1)
        
        # Apply feature scaling
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)  # Scale features
        
        # Rebuild the scaled DataFrame with the target
        iris_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)
        iris_scaled_df['Species'] = y
        
        # Convert the processed DataFrame to JSON
        iris_scaled_json = iris_scaled_df.to_dict(orient="records")
        return JSONResponse(content={"data": iris_scaled_json})
    
    except Exception as e:
        logging.error(f"Error processing dataset: {e}")
        return {"error": f"Failed to process dataset: {e}"}
