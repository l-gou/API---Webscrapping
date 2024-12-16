import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app  # Assurez-vous que c'est là où FastAPI est initialisé

# Client de test pour simuler les appels à l'API
client = TestClient(app)

# Données simulées pour le test
MOCK_PROCESSED_DATA = {
    "data": [
        {"feature1": 5.1, "feature2": 3.5, "feature3": 1.4, "feature4": 0.2, "Species": "Iris-setosa"},
        {"feature1": 4.9, "feature2": 3.0, "feature3": 1.4, "feature4": 0.2, "Species": "Iris-setosa"},
        {"feature1": 6.7, "feature2": 3.1, "feature3": 4.4, "feature4": 1.4, "Species": "Iris-versicolor"},
        {"feature1": 6.3, "feature2": 2.9, "feature3": 5.6, "feature4": 1.8, "Species": "Iris-virginica"},
        {"feature1": 5.8, "feature2": 2.7, "feature3": 5.1, "feature4": 1.9, "Species": "Iris-virginica"},
    ]
}

# Test pour le endpoint /split-data
@patch("src.api.routes.process.process_data")  # Mock de la fonction process_data
def test_split_data(mock_process_data):
    # Configurer le mock pour renvoyer les données simulées
    from fastapi.responses import JSONResponse
    mock_process_data.return_value = JSONResponse(content=MOCK_PROCESSED_DATA)

    # Appeler le endpoint via le client de test
    response = client.get("/split-data")
    assert response.status_code == 200

    # Charger les données JSON de la réponse
    response_data = response.json()

    # Vérifier que les clés attendues sont présentes
    assert "train_data" in response_data
    assert "test_data" in response_data

    train_data = response_data["train_data"]
    test_data = response_data["test_data"]

    # Vérifier que les données d'entraînement et de test ne sont pas vides
    assert len(train_data["X_train"]) > 0
    assert len(train_data["y_train"]) > 0
    assert len(test_data["X_test"]) > 0
    assert len(test_data["y_test"]) > 0

    # Vérifier que les tailles des ensembles respectent la division 80/20
    total_samples = len(MOCK_PROCESSED_DATA["data"])
    expected_train_size = int(total_samples * 0.8)
    expected_test_size = total_samples - expected_train_size

    assert len(train_data["X_train"]) == expected_train_size
    assert len(test_data["X_test"]) == expected_test_size

    # Vérifier que les cibles correspondent à leurs caractéristiques
    assert len(train_data["X_train"]) == len(train_data["y_train"])
    assert len(test_data["X_test"]) == len(test_data["y_test"])
