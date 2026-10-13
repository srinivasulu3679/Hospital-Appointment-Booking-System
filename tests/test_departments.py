def test_list_departments(client):
    response = client.get("/departments/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_nonexistent_department(client):
    response = client.get("/departments/999999")

    assert response.status_code == 404
