def test_refresh_with_invalid_token(client):
    response = client.post(
        "/auth/refresh",
        params={"refresh_token": "invalid-refresh-token"}
    )

    assert response.status_code == 401


def test_logout_requires_authentication(client):
    response = client.post("/auth/logout")

    assert response.status_code == 401
