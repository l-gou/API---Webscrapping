import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))


# Importer le fichier où se trouve votre route (par exemple main.py)
from main import app  # Remplacez `main` par le nom de votre fichier si nécessaire

@pytest.fixture
def client() -> TestClient:
    """
    Test client for integration tests
    """
    client = TestClient(app, base_url="http://testserver")
    return client

class TestDownloadDataset:
    @patch("os.path.exists")
    @patch("opendatasets.download")
    @patch.dict(os.environ, {"KAGGLE_CONFIG_DIR": "/fake/path"})
    def test_download_dataset(self, mock_download, mock_exists, client):
        # Configuration du test : Si le fichier existe déjà, il ne faut pas le télécharger à nouveau
        mock_exists.return_value = False  # Simuler que le fichier n'existe pas

        # Appel à la route pour télécharger le dataset
        response = client.get("/download-dataset")

        # Vérification de la réponse
        assert response.status_code == 200
        assert response.json() == {
            "message": "Dataset downloaded successfully",
            "dataset_location": "/fake/path/iris.csv"
        }
        
        # Vérifier que la fonction `download` a été appelée
        mock_download.assert_called_once_with("uciml/iris", "/fake/path/src/data")

    @patch("os.path.exists")
    @patch("opendatasets.download")
    @patch.dict(os.environ, {"KAGGLE_CONFIG_DIR": "/fake/path"})
    def test_skip_download_when_dataset_exists(self, mock_download, mock_exists, client):
        # Configuration du test : Simuler que le fichier existe déjà
        mock_exists.return_value = True

        # Appel à la route pour télécharger le dataset
        response = client.get("/download-dataset")

        # Vérification de la réponse
        assert response.status_code == 200
        assert response.json() == {
            "message": "Dataset already exists, skipping download.",
            "dataset_location": "/fake/path/iris.csv"
        }
        
        # Vérifier que la fonction `download` n'a pas été appelée
        mock_download.assert_not_called()

    @patch("os.path.exists")
    @patch.dict(os.environ, {"KAGGLE_CONFIG_DIR": "/fake/path"})
    def test_download_dataset_error(self, mock_exists, client):
        # Configurer pour qu'une exception soit lancée
        mock_exists.side_effect = Exception("An error occurred")

        # Appel à la route pour télécharger le dataset
        response = client.get("/download-dataset")

        # Vérification de la réponse en cas d'erreur
        assert response.status_code == 500
        assert "error" in response.json()
        assert response.json()["message"] == "Error downloading dataset"
