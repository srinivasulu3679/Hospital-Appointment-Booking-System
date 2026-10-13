def test_list_doctors(client):
    response = client.get("/doctors/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_nonexistent_doctor(client):
    response = client.get("/doctors/999999")

    assert response.status_code == 404
