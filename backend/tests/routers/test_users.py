from sqlalchemy.orm import Session
from fastapi.testclient import TestClient




def test_read_users_non_admin(client: TestClient):
    res = client.get("/user/")

    assert res.status_code == 200


def test_create_single_user_happy_path(client: TestClient):
    payload = {
        "first_name": "Sam",
        "last_name": "Iam",
        "email": "greeneggs@ham.com",
        "password": "wouldyoulikesomegreeneggsandham",
    }
    res = client.post("/user/", json=payload)
    data = res.json()

    assert res.status_code == 201
    assert data == {"status": "User created successfully"}

