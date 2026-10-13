def test_list_appointments_requires_authentication(client):
    response = client.get("/appointments/my")

    assert response.status_code == 401


def test_create_appointment_requires_authentication(client):
    response = client.post(
        "/appointments/",
        json={
            "doctor_id": 1,
            "appointment_date": "2030-01-15",
            "appointment_time": "10:00:00"
        }
    )

    assert response.status_code == 401
