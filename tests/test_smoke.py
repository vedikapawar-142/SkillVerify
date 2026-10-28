from app import create_app
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


def test_home_page_loads():
    app = create_app(TestConfig)
    client = app.test_client()
    assert client.get("/").status_code == 200


def test_register_and_login():
    app = create_app(TestConfig)
    client = app.test_client()
    client.post("/register", data={"name": "Test", "email": "t@example.com", "password": "secret1", "role": "candidate"})
    resp = client.post("/login", data={"email": "t@example.com", "password": "secret1"}, follow_redirects=True)
    assert b"Welcome, Test" in resp.data
