def test_list_doctor_availability(client):
    response = client.get("/doctor-availability/doctor/999999")

    assert response.status_code in (200, 404)


def test_create_availability_requires_authentication(client):
    response = client.post(
        "/doctor-availability/",
        json={
            "doctor_id": 1,
            "available_date": "2030-01-15",
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_available": True
        }
    )

    assert response.status_code == 401
