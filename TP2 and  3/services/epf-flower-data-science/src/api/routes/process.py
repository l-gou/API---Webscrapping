import os
import pandas as pd
import logging
from fastapi import APIRouter
from sklearn.preprocessing import StandardScaler
from fastapi.responses import JSONResponse

from src.api.routes import load  # Assuming load.py is in the src/api/routes directory


router = APIRouter()


@router.get("/process-data", name="Process Iris Dataset")
def process_data():
    data_dir = "TP2 and  3/services/epf-flower-data-science/src/data"
    iris_path = os.path.join(data_dir, "iris.csv")

    if not os.path.exists(iris_path):
        return {"error": "Dataset not found. Please download the dataset first."}

    try:
        # Get the dataset from the /load-iris-dataset endpoint (via load function)
        iris_response = load.load_iris_dataset()  # Call the load function to get the data

        # Check if the response contains an error
        if isinstance(iris_response, dict) and "error" in iris_response:
            return iris_response  # Return the error if it exists
        
        # Get the 'data' part of the response (which is a dictionary)
        iris_json = iris_response["data"]
        
        # Convert the processed data back into a DataFrame
        iris_df = pd.DataFrame(iris_json)
        
        # Separate features and target
        X = iris_df.iloc[:, :-1]  # Features (exclude the last column 'species')
        y = iris_df['Species']    # Target (species column)
        
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
