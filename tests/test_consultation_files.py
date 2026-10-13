def test_list_consultation_files_requires_authentication(client):
    response = client.get("/consultation-files/1")

    assert response.status_code == 401
