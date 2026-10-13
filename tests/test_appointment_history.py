def test_list_appointment_history_requires_authentication(client):
    response = client.get("/appointment-history/1")

    assert response.status_code == 401


def test_get_unknown_appointment_history(client):
    response = client.get("/appointment-history/999999")

    assert response.status_code == 401
