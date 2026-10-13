def test_list_consultations_requires_authentication(client):
    response = client.get("/consultations/")

    assert response.status_code == 401


def test_get_nonexistent_consultation(client):
    response = client.get("/consultations/999999")

    assert response.status_code == 401
