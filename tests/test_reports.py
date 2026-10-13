def test_dashboard_report_requires_authentication(client):
    response = client.get("/reports/dashboard")

    assert response.status_code == 401


def test_doctor_report_requires_authentication(client):
    response = client.get("/reports/doctors/1/appointments")

    assert response.status_code == 401
