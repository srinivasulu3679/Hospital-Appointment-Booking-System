def test_list_doctor_leaves_for_unknown_doctor(client):
    response = client.get("/doctor-leaves/999999")

    assert response.status_code == 404


def test_create_doctor_leave_requires_authentication(client):
    response = client.post(
        "/doctor-leaves/",
        json={
            "doctor_id": 1,
            "start_date": "2030-01-15",
            "end_date": "2030-01-16",
            "reason": "Personal leave"
        }
    )

    assert response.status_code == 401
