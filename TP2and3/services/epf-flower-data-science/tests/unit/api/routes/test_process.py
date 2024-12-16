import pytest
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
from unittest.mock import patch
from main import app  # Assurez-vous que c'est là où FastAPI est initialisé (remplacez si nécessaire)

# Client de test pour simuler les appels à l'API
client = TestClient(app)

# Données simulées pour le test
MOCK_IRIS_DATA = {
    "data": [
        {"SepalLengthCm": 5.1, "SepalWidthCm": 3.5, "PetalLengthCm": 1.4, "PetalWidthCm": 0.2, "Species": "Iris-setosa"},
        {"SepalLengthCm": 4.9, "SepalWidthCm": 3.0, "PetalLengthCm": 1.4, "PetalWidthCm": 0.2, "Species": "Iris-setosa"},
    ]
}

# Test pour le endpoint /process-data
@patch("src.api.routes.load.load_iris_dataset")  # Mock de la fonction load_iris_dataset
def test_process_data(mock_load_iris_dataset):
    # Configurer le mock pour renvoyer les données simulées
    mock_load_iris_dataset.return_value = JSONResponse(content=MOCK_IRIS_DATA)
    
    # Appeler le endpoint via le client de test
    response = client.get("/process-data")
    
    # Assurez-vous que la réponse est réussie
    assert response.status_code == 200

    # Charger les données JSON de la réponse
    response_data = response.json()

    # Vérifications de base sur le format des données
    assert "data" in response_data
    processed_data = response_data["data"]
    
    # Vérifier qu'il y a bien des lignes dans les données transformées
    assert len(processed_data) == len(MOCK_IRIS_DATA["data"])

    # Vérifier que les colonnes transformées correspondent à ce qui est attendu
    expected_columns = ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm", "Species"]
    for row in processed_data:
        assert all(col in row for col in expected_columns)
    
    # Vérifier que la colonne 'Species' est intacte
    assert all(row["Species"] in ["Iris-setosa"] for row in processed_data)
