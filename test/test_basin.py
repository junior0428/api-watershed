# test/test_basin.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_delineate_watershed():
    response = client.post("/basin/delineation/", json={"latitude":38.89038, "longitude":-4.08972})
    assert response.status_code == 200
    assert "catchment" in response.json()
