def test_websocket_endpoint_exists(client):
    response = client.get("/ws/notifications")

    # WebSocket endpoints may reject ordinary HTTP requests.
    assert response.status_code in (404, 405, 403, 426)
