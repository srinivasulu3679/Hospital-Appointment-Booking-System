def test_register_patient(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test Patient",
            "email": "patient_test@example.com",
            "phone": "9876543210",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "patient_test@example.com"
    assert data["role"] == "Patient"
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    user_data = {
        "full_name": "Test Patient",
        "email": "duplicate_test@example.com",
        "phone": "9876543211",
        "password": "TestPassword123"
    }

    first_response = client.post("/auth/register", json=user_data)
    second_response = client.post("/auth/register", json=user_data)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "WrongPassword123"
        }
    )

    assert response.status_code == 401
