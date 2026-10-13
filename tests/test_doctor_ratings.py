def test_list_doctor_ratings(client):
    response = client.get("/doctor-ratings/doctor/999999")

    assert response.status_code in (200, 404)


def test_create_doctor_rating_requires_authentication(client):
    response = client.post(
        "/doctor-ratings/",
        json={
            "appointment_id": 1,
            "rating": 5,
            "review": "Excellent service"
        }
    )

    assert response.status_code == 401
