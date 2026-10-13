def test_list_prescriptions_requires_authentication(client):
    response = client.get("/prescriptions/")

    assert response.status_code == 401


def test_create_prescription_requires_authentication(client):
    response = client.post(
        "/prescriptions/",
        json={
            "consultation_id": 1,
            "medicines": "Medicine A",
            "instructions": "Take as directed"
        }
    )

    assert response.status_code == 401
