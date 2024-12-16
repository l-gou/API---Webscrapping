import os
import pandas as pd
from fastapi import APIRouter
from typing import Dict, Union
import logging
from fastapi.responses import JSONResponse

router = APIRouter()

# New endpoint to load the dataset as a pandas DataFrame and return it as JSON
@router.get("/load-iris-dataset", name="Load Iris Dataset")
def load_iris_dataset() -> Union[JSONResponse, Dict[str, str]]:
    """
    Load the Iris dataset as a pandas DataFrame and return it as a JSON response.

    Endpoint:
        GET /load-iris-dataset

    Returns:
        Union[JSONResponse, Dict[str, str]]: A JSON response containing the Iris dataset in JSON format, 
        or an error message if the dataset is not found or cannot be loaded.
    """    
    data_dir = "TP2and3/services/epf-flower-data-science/src/data"
    iris_path = os.path.join(data_dir, "iris.csv")

    if not os.path.exists(iris_path):
        return {"error": "Dataset not found. Please download the dataset first."}

    # Load the dataset into a pandas DataFrame
    try:
        iris_df = pd.read_csv(iris_path)
        # Convert the DataFrame to a dictionary (using to_dict() to make it JSON serializable)
        iris_json = iris_df.to_dict(orient="records")
        return JSONResponse(content={"data": iris_json})
    except Exception as e:
        logging.error(f"Error loading dataset: {e}")
        return {"error": f"Failed to load dataset: {e}"}
