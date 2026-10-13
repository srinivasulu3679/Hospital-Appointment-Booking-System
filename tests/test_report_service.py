from app.services.report_service import get_dashboard_report


def test_dashboard_report_returns_expected_sections(db):
    report = get_dashboard_report(db)

    assert isinstance(report, dict)
    assert "patients" in report
    assert "doctors" in report
    assert "departments" in report
    assert "appointments" in report
