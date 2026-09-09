import os

os.environ["SECRET_KEY"] = "test-secret-at-least-32-characters-long"
os.environ["DATABASE_URL"] = "sqlite://"
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Base.metadata.create_all(engine)
Session = sessionmaker(engine)


def override_db():
    with Session() as db:
        yield db


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def account(email):
    assert client.post("/users/", json={"email": email, "password": "A-long-password-123"}).status_code == 201
    r = client.post("/login", data={"username": email, "password": "A-long-password-123"})
    assert r.status_code == 200
    return {"Authorization": "Bearer " + r.json()["access_token"]}


def test_workflow():
    a, b = account("a@example.com"), account("b@example.com")
    assert client.get("/posts/").status_code == 401
    assert (
        client.post("/users/", json={"email": "a@example.com", "password": "A-long-password-123"}).status_code
        == 409
    )
    r = client.post("/posts/", headers=a, json={"title": "Draft", "content": "Private", "published": False})
    assert r.status_code == 201
    pid = r.json()["id"]
    assert client.get(f"/posts/{pid}", headers=b).status_code == 404
    assert client.get("/posts/", headers=b).json() == []
    assert client.put(f"/posts/{pid}", headers=b, json={"title": "No", "content": "No"}).status_code == 403
    assert (
        client.put(f"/posts/{pid}", headers=a, json={"title": "Live", "content": "Hello"}).status_code == 200
    )
    assert client.post("/vote/", headers=b, json={"post_id": pid, "dir": -1}).status_code == 422
    assert client.post("/vote/", headers=b, json={"post_id": pid, "dir": 1}).status_code == 201
    assert client.post("/vote/", headers=b, json={"post_id": pid, "dir": 1}).status_code == 409
    row = client.get(f"/posts/{pid}", headers=b).json()
    assert row["votes"] == 1 and row["voted"] is True
    assert client.post("/vote/", headers=b, json={"post_id": pid, "dir": 0}).status_code == 201
    assert client.get("/posts/?limit=10000", headers=a).status_code == 422
    assert client.delete(f"/posts/{pid}", headers=b).status_code == 403
    assert client.delete(f"/posts/{pid}", headers=a).status_code == 204
    assert client.get("/users/me", headers=a).status_code == 200
    assert client.get("/health").status_code == 200
