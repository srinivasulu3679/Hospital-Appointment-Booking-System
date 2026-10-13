
import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()


def send_email(recipient: str, subject: str, body: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    # Support both SMTP_EMAIL and SMTP_USERNAME
    smtp_username = (
        os.getenv("SMTP_EMAIL")
        or os.getenv("SMTP_USERNAME")
    )

    smtp_password = os.getenv("SMTP_PASSWORD")

    sender_email = (
        os.getenv("SENDER_EMAIL")
        or smtp_username
    )

    # Validate SMTP configuration
    if not smtp_host or not sender_email:
        print("Email skipped: SMTP settings are missing.")
        return False

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=15
        ) as server:
            server.starttls()

            if smtp_username and smtp_password:
                server.login(
                    smtp_username,
                    smtp_password
                )

            server.send_message(message)

        print("Email sent successfully.")
        return True

    except (smtplib.SMTPException, OSError, ValueError) as exc:
        print(f"Email sending failed: {exc}")
        return False
