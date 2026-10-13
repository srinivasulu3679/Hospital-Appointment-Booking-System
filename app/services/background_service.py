
from fastapi import BackgroundTasks

from app.services.email_service import send_email


def queue_email(
    background_tasks: BackgroundTasks,
    recipient: str,
    subject: str,
    body: str,
) -> None:
    background_tasks.add_task(
        send_email,
        recipient,
        subject,
        body,
    )


def queue_appointment_confirmation(
    background_tasks: BackgroundTasks,
    recipient: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    appointment_time: str,
) -> None:
    subject = "Appointment Confirmation"

    body = (
        f"Hello {patient_name},\n\n"
        "Your hospital appointment has been booked successfully.\n\n"
        f"Doctor: {doctor_name}\n"
        f"Date: {appointment_date}\n"
        f"Time: {appointment_time}\n\n"
        "Please arrive a little early for your appointment.\n\n"
        "Regards,\nHospital Appointment Booking System"
    )

    queue_email(
        background_tasks,
        recipient,
        subject,
        body,
    )
