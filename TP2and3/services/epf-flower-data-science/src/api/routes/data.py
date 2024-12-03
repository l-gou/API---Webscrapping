import os
import opendatasets as od
from fastapi import APIRouter
import logging

router = APIRouter()

# Setup logging
logging.basicConfig(level=logging.INFO)

@router.get("/download-dataset", name="Download Iris Dataset")
def download_dataset():
    try:
        # Specify the path to the folder where kaggle.json is located
        kaggle_json_path = "TP2and3/services/epf-flower-data-science/" 

        # Set the KAGGLE_CONFIG_DIR environment variable to the path of the folder containing kaggle.json
        os.environ['KAGGLE_CONFIG_DIR'] = os.path.abspath(kaggle_json_path)

        # Dataset identifier (not the full URL)
        dataset_id = "uciml/iris"  # Correct Kaggle dataset identifier
        data_dir = "TP2and3/services/epf-flower-data-science/src/data"

        # Check if the dataset is already downloaded
        if not os.path.exists(os.path.join(data_dir, "iris.csv")):
            logging.info(f"Downloading dataset {dataset_id}...")
            od.download(dataset_id, data_dir)
            logging.info("Dataset downloaded successfully")
        else:
            logging.info("Dataset already exists, skipping download.")

        return {"message": "Dataset downloaded successfully", "dataset_location": os.path.join(data_dir, "iris.csv")}
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return {"message": "Error downloading dataset", "error": str(e)}
