def test_list_doctor_queue_requires_authentication(client):
    response = client.get("/doctor-queue/doctor/1")

    assert response.status_code == 401


def test_add_to_queue_requires_authentication(client):
    response = client.post(
        "/doctor-queue/",
        json={
            "doctor_id": 1,
            "appointment_id": 1,
            "token_number": 1
        }
    )

    assert response.status_code == 401
