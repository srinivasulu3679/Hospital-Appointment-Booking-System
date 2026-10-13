def test_list_notifications_requires_authentication(client):
    response = client.get("/notifications/")

    assert response.status_code == 401


def test_mark_notification_read_requires_authentication(client):
    response = client.patch("/notifications/999999/read")

    assert response.status_code == 401
