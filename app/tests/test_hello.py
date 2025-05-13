from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_send_hello_success():
    response = client.get("/hello", params={"name": "Cesar"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Cesar"}

def test_send_hello_missing_name():
    response = client.get("/hello")
    assert response.status_code == 422
