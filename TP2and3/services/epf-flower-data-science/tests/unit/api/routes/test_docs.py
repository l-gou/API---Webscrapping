import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from src.api import router 

# Créez une instance de FastAPI avec le router
app = FastAPI()
app.include_router(router)

@pytest.fixture
def client() -> TestClient:
    """
    Test client for integration tests
    """
    return TestClient(app)

class TestRedirectToDocs:
    def test_redirect_to_docs(self, client):
        # Effectuer une requête GET sur la route "/"
        response = client.get("/")

        # Vérifier que la réponse est une redirection
        assert response.status_code == 307
        assert response.headers["Location"] == "/docs"
