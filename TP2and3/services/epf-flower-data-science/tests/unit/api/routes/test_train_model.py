import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app  # Assurez-vous que c'est là où FastAPI est initialisé
import joblib

# Client de test pour simuler les appels à l'API
client = TestClient(app)

# Données simulées pour le test
MOCK_SPLIT_DATA = {
    "train_data": {
        "X_train": [
            {"feature1": 1.0, "feature2": 2.0},
            {"feature1": 1.5, "feature2": 1.8},
        ],
        "y_train": [0, 1],
    },
    "test_data": {
        "X_test": [
            {"feature1": 1.1, "feature2": 2.1},
        ],
        "y_test": [0],
    },
}

MOCK_MODEL_PARAMS = {
    "RandomForestClassifier": {"n_estimators": 10, "max_depth": 3},
    "SVC": {"kernel": "linear", "C": 1.0},
}

# Test pour le endpoint /train-model
@patch("src.api.routes.split.split_data")  # Mock de la fonction split_data
@patch("src.api.routes.train.load_model_parameters")  # Mock de la fonction load_model_parameters
def test_train_model(mock_load_model_parameters, mock_split_data, tmpdir):
    # Configurer le mock pour les données de split
    mock_split_data.return_value = MOCK_SPLIT_DATA

    # Configurer le mock pour les paramètres du modèle
    mock_load_model_parameters.return_value = MOCK_MODEL_PARAMS

    # Créer un chemin temporaire pour sauvegarder les modèles
    model_dir = tmpdir.mkdir("models")
    with patch("os.makedirs") as mock_makedirs, patch("os.path.join", side_effect=lambda *args: os.path.join(model_dir, *args)):

        # Configurer le mock pour éviter la création de répertoires
        mock_makedirs.return_value = None

        # Appeler le endpoint avec un modèle spécifique
        response = client.get("/train-model?model_name=RandomForestClassifier")
        assert response.status_code == 200

        # Vérifier la réponse JSON
        response_data = response.json()
        assert "message" in response_data
        assert "model_path" in response_data

        # Vérifier que le modèle est sauvegardé
        model_save_path = response_data["model_path"]
        assert os.path.exists(model_save_path)

        # Charger le modèle sauvegardé pour validation
        saved_model = joblib.load(model_save_path)
        assert saved_model is not None
        assert saved_model.__class__.__name__ == "RandomForestClassifier"
