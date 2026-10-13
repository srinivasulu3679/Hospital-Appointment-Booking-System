from unittest.mock import patch

from app.services.email_service import send_email


def test_send_email_without_smtp_configuration():
    with patch.dict(
        "os.environ",
        {
            "SMTP_HOST": "",
            "SMTP_USERNAME": "",
            "SMTP_PASSWORD": "",
            "SENDER_EMAIL": "",
        },
        clear=False,
    ):
        result = send_email(
            recipient="test@example.com",
            subject="Test Email",
            body="Test message",
        )

    assert result is False
