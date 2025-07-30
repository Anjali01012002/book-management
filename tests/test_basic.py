import pytest
from app import app as flask_app
from models import db, User, Book

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_register(client):
    response = client.post('/api/register', json={"username": "testuser", "password": "testpass", "role": "admin"})
    assert response.status_code == 201

def test_login(client):
    client.post('/api/register', json={"username": "testuser", "password": "testpass", "role": "admin"})
    response = client.post('/api/login', json={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_create_book(client):
    client.post('/api/register', json={"username": "testuser", "password": "testpass", "role": "librarian"})
    response = client.post('/api/login', json={"username": "testuser", "password": "testpass"})
    token = response.get_json()["access_token"]
    response = client.post('/api/books', json={"title": "Test Book", "author": "Test Author", "isbn": "9876543210123", "quantity": 10},
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201