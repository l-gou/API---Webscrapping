import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import pandas as pd
from src.api import router  

# Créez une instance de FastAPI avec le router
from fastapi import FastAPI
app = FastAPI()
app.include_router(router)

@pytest.fixture
def client() -> TestClient:
    """
    Test client for integration tests
    """
    return TestClient(app)

class TestLoadIrisDataset:
    
    @patch("os.path.exists")
    @patch("pandas.read_csv")
    def test_load_iris_dataset_success(self, mock_read_csv, mock_exists, client):
        # Simuler que le fichier iris.csv existe
        mock_exists.return_value = True
        # Simuler que pandas.read_csv retourne un DataFrame correct
        mock_df = pd.DataFrame({
            'sepal_length': [5.1, 4.9],
            'sepal_width': [3.5, 3.0],
            'petal_length': [1.4, 1.4],
            'petal_width': [0.2, 0.2],
            'species': ['setosa', 'setosa']
        })
        mock_read_csv.return_value = mock_df

        # Appeler l'endpoint pour charger le dataset
        response = client.get("/load-iris-dataset")

        # Vérifier que le code de statut est 200
        assert response.status_code == 200

        # Vérifier que les données retournées sont correctes
        assert "data" in response.json()
        assert len(response.json()["data"]) == 2  # Nous avons deux lignes dans le DataFrame mocké
        assert response.json()["data"][0]["sepal_length"] == 5.1

    @patch("os.path.exists")
    def test_load_iris_dataset_not_found(self, mock_exists, client):
        # Simuler que le fichier iris.csv n'existe pas
        mock_exists.return_value = False

        # Appeler l'endpoint pour charger le dataset
        response = client.get("/load-iris-dataset")

        # Vérifier que le code de statut est 200 et que le message d'erreur est correct
        assert response.status_code == 200
        assert response.json() == {"error": "Dataset not found. Please download the dataset first."}

    @patch("os.path.exists")
    @patch("pandas.read_csv")
    def test_load_iris_dataset_error(self, mock_read_csv, mock_exists, client):
        # Simuler que le fichier iris.csv existe
        mock_exists.return_value = True
        # Simuler que pandas.read_csv lève une exception
        mock_read_csv.side_effect = Exception("Error reading CSV file")

        # Appeler l'endpoint pour charger le dataset
        response = client.get("/load-iris-dataset")

        # Vérifier que le code de statut est 200 et que le message d'erreur est correct
        assert response.status_code == 200
        assert "error" in response.json()
        assert response.json()["error"] == "Failed to load dataset: Error reading CSV file"
