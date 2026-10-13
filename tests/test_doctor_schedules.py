def test_list_doctor_schedules(client):
    response = client.get("/doctor-schedules/999999")

    assert response.status_code == 404


def test_create_schedule_requires_authentication(client):
    response = client.post(
        "/doctor-schedules/",
        json={
            "doctor_id": 1,
            "day_of_week": 1,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "slot_duration_minutes": 30
        }
    )

    assert response.status_code == 401
