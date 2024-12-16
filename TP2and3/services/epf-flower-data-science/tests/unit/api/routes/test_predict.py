import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
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

class TestPredict:

    @patch("your_module.load_trained_model")  # Remplacez `your_module` par le bon nom de module
    @patch("joblib.load")
    def test_predict_success(self, mock_joblib_load, mock_load_trained_model, client):
        # Simuler que le modèle est correctement chargé
        mock_model = MagicMock()
        mock_model.predict.return_value = [0]  # Simuler une prédiction
        mock_load_trained_model.return_value = mock_model

        # Définir les données d'entrée pour la prédiction
        input_data = {
            "SepalLengthCm": 5.1,
            "SepalWidthCm": 3.5,
            "PetalLengthCm": 1.4,
            "PetalWidthCm": 0.2
        }

        # Appeler l'endpoint pour faire une prédiction
        response = client.post("/predict?model_name=iris_model", json=input_data)

        # Vérifier que la réponse est correcte
        assert response.status_code == 200
        assert "predictions" in response.json()
        assert response.json()["predictions"] == [0]  # La prédiction simulée

    @patch("your_module.load_trained_model")  # Remplacez `your_module` par le bon nom de module
    def test_predict_model_not_found(self, mock_load_trained_model, client):
        # Simuler que le modèle n'existe pas
        mock_load_trained_model.side_effect = FileNotFoundError("Model file not found")

        # Définir les données d'entrée pour la prédiction
        input_data = {
            "SepalLengthCm": 5.1,
            "SepalWidthCm": 3.5,
            "PetalLengthCm": 1.4,
            "PetalWidthCm": 0.2
        }

        # Appeler l'endpoint pour faire une prédiction avec un modèle inexistant
        response = client.post("/predict?model_name=non_existent_model", json=input_data)

        # Vérifier que l'erreur 404 est renvoyée
        assert response.status_code == 404
        assert response.json() == {"detail": "Model file not found"}

    @patch("your_module.load_trained_model")  # Remplacez `your_module` par le bon nom de module
    @patch("joblib.load")
    def test_predict_error_during_prediction(self, mock_joblib_load, mock_load_trained_model, client):
        # Simuler que le modèle est correctement chargé
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("Error during prediction")
        mock_load_trained_model.return_value = mock_model

        # Définir les données d'entrée pour la prédiction
        input_data = {
            "SepalLengthCm": 5.1,
            "SepalWidthCm": 3.5,
            "PetalLengthCm": 1.4,
            "PetalWidthCm": 0.2
        }

        # Appeler l'endpoint pour faire une prédiction
        response = client.post("/predict?model_name=iris_model", json=input_data)

        # Vérifier que l'erreur 500 est renvoyée
        assert response.status_code == 500
        assert response.json() == {"detail": "Failed to make prediction: Error during prediction"}
