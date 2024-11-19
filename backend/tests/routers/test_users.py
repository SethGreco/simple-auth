from fastapi.testclient import TestClient


def test_read_users_non_admin(client: TestClient):
    res = client.get("/user/")
    assert res.status_code == 200


def test_create_single_user_happy_path(client: TestClient):
    payload = {
        "firstName": "Sam",
        "lastName": "Iam",
        "email": "greeneggs@ham.com",
        "password": "1Wouldyoulikesomegreeneggsandham",
    }
    res = client.post("/user/", json=payload)
    data = res.json()

    assert res.status_code == 201
    assert data == {"detail": "User created successfully"}
