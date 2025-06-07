import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_valid_query(client):
    response = client.post('/query', json={"query": "List cancer patients under 30"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["filters"]["condition"] == ["cancer"]
    assert data["filters"]["age"]["operator"] == "lt"
    assert data["filters"]["age"]["value"] == 30

def test_empty_query(client):
    response = client.post('/query', json={"query": ""})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "'query' cannot be empty"


def test_missing_query_field(client):
    response = client.post('/query', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_non_string_query(client):
    response = client.post('/query', json={"query": 12345})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_multiple_conditions(client):
    response = client.post('/query', json={"query": "List diabetic and cancer patients over 50"})
    assert response.status_code == 200
    data = response.get_json()
    assert "diabetic" in data["filters"]["condition"]
    assert "cancer" in data["filters"]["condition"]
    assert data["filters"]["age"]["operator"] == "gt"
    assert data["filters"]["age"]["value"] == 50


