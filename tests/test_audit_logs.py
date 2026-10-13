def test_list_audit_logs_requires_authentication(client):
    response = client.get("/audit-logs/")

    assert response.status_code == 401


def test_get_audit_log_requires_authentication(client):
    response = client.get("/audit-logs/999999")

    assert response.status_code == 401
