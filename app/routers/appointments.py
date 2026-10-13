
from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user, require_roles
from app.models.appointment import Appointment
from app.models.appointment_history import AppointmentHistory
from app.models.doctor import Doctor
from app.models.doctor_leave import DoctorLeave
from app.models.doctor_schedule import DoctorSchedule
from app.models.user import User
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentReschedule,
    AppointmentStatusUpdate,
)
from app.services.audit_service import create_audit_log
from app.services.notification_service import create_notification
from app.services.background_service import queue_appointment_confirmation
from app.utils.connection_manager import manager

router = APIRouter(prefix="/appointments", tags=["Appointments"])


def check_doctor_slot(
    db: Session,
    doctor_id: int,
    appt_date: date,
    appt_time,
):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active.is_(True),
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Active doctor not found",
        )

    schedule = db.query(DoctorSchedule).filter(
        DoctorSchedule.doctor_id == doctor_id,
        DoctorSchedule.day_of_week == appt_date.weekday(),
        DoctorSchedule.is_active.is_(True),
    ).first()

    if not schedule:
        raise HTTPException(
            status_code=400,
            detail="Doctor is not scheduled on this day",
        )

    if not (schedule.start_time <= appt_time < schedule.end_time):
        raise HTTPException(
            status_code=400,
            detail="Time is outside doctor's schedule",
        )

    if schedule.break_start and schedule.break_end:
        if schedule.break_start <= appt_time < schedule.break_end:
            raise HTTPException(
                status_code=400,
                detail="Time falls during doctor's break",
            )

    doctor_on_leave = db.query(DoctorLeave).filter(
        DoctorLeave.doctor_id == doctor_id,
        DoctorLeave.start_date <= appt_date,
        DoctorLeave.end_date >= appt_date,
    ).first()

    if doctor_on_leave:
        raise HTTPException(
            status_code=400,
            detail="Doctor is on leave that day",
        )

    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appt_date,
        Appointment.appointment_time == appt_time,
        Appointment.status != "Cancelled",
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=409,
            detail="Appointment slot is already booked",
        )


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=201,
)
def book_appointment(
    data: AppointmentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Patient", "Admin")
    ),
):
    if data.appointment_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Appointment date cannot be in the past",
        )

    check_doctor_slot(
        db,
        data.doctor_id,
        data.appointment_date,
        data.appointment_time,
    )

    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id
    ).first()

    appointment = Appointment(
        patient_id=current_user.id,
        doctor_id=data.doctor_id,
        appointment_date=data.appointment_date,
        appointment_time=data.appointment_time,
        consultation_fee=doctor.consultation_fee,
        status="Booked",
    )

    db.add(appointment)
    db.flush()

    db.add(
        AppointmentHistory(
            appointment_id=appointment.id,
            changed_by=current_user.id,
            old_status=None,
            new_status="Booked",
            remarks="Appointment created",
        )
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="CREATE",
        entity_type="Appointment",
        entity_id=appointment.id,
        details={
            "status": "Booked",
            "doctor_id": data.doctor_id,
            "appointment_date": str(data.appointment_date),
            "appointment_time": str(data.appointment_time),
        },
    )

    patient_notification = create_notification(
        db=db,
        user_id=current_user.id,
        title="Appointment Booked",
        message=(
            f"Your appointment with doctor {doctor.id} "
            f"on {data.appointment_date} at {data.appointment_time} "
            "has been booked."
        ),
        notification_type="Appointment",
        appointment_id=appointment.id,
    )

    doctor_notification = None

    if doctor.user_id and doctor.user_id != current_user.id:
        doctor_notification = create_notification(
            db=db,
            user_id=doctor.user_id,
            title="New Appointment",
            message=(
                f"A new appointment has been booked for "
                f"{data.appointment_date} at {data.appointment_time}."
            ),
            notification_type="Appointment",
            appointment_id=appointment.id,
        )

    db.commit()
    db.refresh(appointment)
    db.refresh(patient_notification)

    background_tasks.add_task(
        manager.send_to_user,
        current_user.id,
        {
            "type": "notification",
            "id": patient_notification.id,
            "title": patient_notification.title,
            "message": patient_notification.message,
            "appointment_id": appointment.id,
        },
    )

    if doctor_notification:
        db.refresh(doctor_notification)

        background_tasks.add_task(
            manager.send_to_user,
            doctor.user_id,
            {
                "type": "notification",
                "id": doctor_notification.id,
                "title": doctor_notification.title,
                "message": doctor_notification.message,
                "appointment_id": appointment.id,
            },
        )

    # Send appointment confirmation email in the background.
    if current_user.email:
        queue_appointment_confirmation(
            background_tasks=background_tasks,
            recipient=current_user.email,
            patient_name=current_user.username,
            doctor_name=f"Doctor #{doctor.id}",
            appointment_date=str(appointment.appointment_date),
            appointment_time=str(appointment.appointment_time),
        )

    return appointment


@router.get("/my", response_model=list[AppointmentResponse])
def my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Appointment)

    if current_user.role == "Patient":
        query = query.filter(
            Appointment.patient_id == current_user.id
        )

    elif current_user.role == "Doctor":
        doctor = db.query(Doctor).filter(
            Doctor.user_id == current_user.id
        ).first()

        if not doctor:
            return []

        query = query.filter(
            Appointment.doctor_id == doctor.id
        )

    return query.order_by(
        Appointment.appointment_date,
        Appointment.appointment_time,
    ).all()


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse,
)
def update_appointment_status(
    appointment_id: int,
    data: AppointmentStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found",
        )

    doctor = db.query(Doctor).filter(
        Doctor.id == appointment.doctor_id
    ).first()

    allowed = (
        current_user.role == "Admin"
        or (
            current_user.role == "Patient"
            and appointment.patient_id == current_user.id
            and data.status == "Cancelled"
        )
        or (
            current_user.role == "Doctor"
            and doctor is not None
            and doctor.user_id == current_user.id
            and data.status in (
                "Confirmed",
                "Completed",
                "No Show",
            )
        )
    )

    if not allowed:
        raise HTTPException(
            status_code=403,
            detail="You cannot change this appointment status",
        )

    if appointment.status in ("Cancelled", "Completed", "No Show"):
        raise HTTPException(
            status_code=400,
            detail="Appointment is already finalized",
        )

    if data.status == "Cancelled" and not data.cancellation_reason:
        raise HTTPException(
            status_code=400,
            detail="Cancellation reason is required",
        )

    old_status = appointment.status
    appointment.status = data.status

    if data.status == "Cancelled":
        appointment.cancellation_reason = data.cancellation_reason

    db.add(
        AppointmentHistory(
            appointment_id=appointment.id,
            changed_by=current_user.id,
            old_status=old_status,
            new_status=data.status,
            remarks=data.cancellation_reason,
        )
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="UPDATE_STATUS",
        entity_type="Appointment",
        entity_id=appointment.id,
        details={
            "old_status": old_status,
            "new_status": data.status,
        },
    )

    patient_notification = create_notification(
        db=db,
        user_id=appointment.patient_id,
        title="Appointment Status Updated",
        message=(
            f"Your appointment #{appointment.id} status changed "
            f"from {old_status} to {data.status}."
        ),
        notification_type="Appointment",
        appointment_id=appointment.id,
    )

    doctor_notification = None

    if doctor and doctor.user_id != current_user.id:
        doctor_notification = create_notification(
            db=db,
            user_id=doctor.user_id,
            title="Appointment Status Updated",
            message=(
                f"Appointment #{appointment.id} status changed "
                f"from {old_status} to {data.status}."
            ),
            notification_type="Appointment",
            appointment_id=appointment.id,
        )

    db.commit()
    db.refresh(appointment)
    db.refresh(patient_notification)

    background_tasks.add_task(
        manager.send_to_user,
        appointment.patient_id,
        {
            "type": "notification",
            "id": patient_notification.id,
            "title": patient_notification.title,
            "message": patient_notification.message,
            "appointment_id": appointment.id,
        },
    )

    if doctor_notification:
        db.refresh(doctor_notification)

        background_tasks.add_task(
            manager.send_to_user,
            doctor.user_id,
            {
                "type": "notification",
                "id": doctor_notification.id,
                "title": doctor_notification.title,
                "message": doctor_notification.message,
                "appointment_id": appointment.id,
            },
        )

    return appointment


@router.patch(
    "/{appointment_id}/reschedule",
    response_model=AppointmentResponse,
)
def reschedule_appointment(
    appointment_id: int,
    data: AppointmentReschedule,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id
    ).first()

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found",
        )

    if (
        current_user.role != "Admin"
        and appointment.patient_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You cannot reschedule this appointment",
        )

    if appointment.status not in ("Booked", "Confirmed"):
        raise HTTPException(
            status_code=400,
            detail="Only active appointments can be rescheduled",
        )

    if appointment.reschedule_count >= 3:
        raise HTTPException(
            status_code=400,
            detail="Reschedule limit reached",
        )

    if data.appointment_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Appointment date cannot be in the past",
        )

    check_doctor_slot(
        db,
        appointment.doctor_id,
        data.appointment_date,
        data.appointment_time,
    )

    old_date = appointment.appointment_date
    old_time = appointment.appointment_time
    old_status = appointment.status

    appointment.appointment_date = data.appointment_date
    appointment.appointment_time = data.appointment_time
    appointment.reschedule_count += 1

    db.add(
        AppointmentHistory(
            appointment_id=appointment.id,
            changed_by=current_user.id,
            old_status=old_status,
            new_status=old_status,
            remarks="Appointment rescheduled",
        )
    )

    create_audit_log(
        db=db,
        user_id=current_user.id,
        action="RESCHEDULE",
        entity_type="Appointment",
        entity_id=appointment.id,
        details={
            "old_date": str(old_date),
            "old_time": str(old_time),
            "new_date": str(data.appointment_date),
            "new_time": str(data.appointment_time),
        },
    )

    patient_notification = create_notification(
        db=db,
        user_id=appointment.patient_id,
        title="Appointment Rescheduled",
        message=(
            f"Appointment #{appointment.id} is now scheduled for "
            f"{data.appointment_date} at {data.appointment_time}."
        ),
        notification_type="Appointment",
        appointment_id=appointment.id,
    )

    doctor = db.query(Doctor).filter(
        Doctor.id == appointment.doctor_id
    ).first()

    doctor_notification = None

    if doctor and doctor.user_id != current_user.id:
        doctor_notification = create_notification(
            db=db,
            user_id=doctor.user_id,
            title="Appointment Rescheduled",
            message=(
                f"Appointment #{appointment.id} is now scheduled for "
                f"{data.appointment_date} at {data.appointment_time}."
            ),
            notification_type="Appointment",
            appointment_id=appointment.id,
        )

    db.commit()
    db.refresh(appointment)
    db.refresh(patient_notification)

    background_tasks.add_task(
        manager.send_to_user,
        appointment.patient_id,
        {
            "type": "notification",
            "id": patient_notification.id,
            "title": patient_notification.title,
            "message": patient_notification.message,
            "appointment_id": appointment.id,
        },
    )

    if doctor_notification:
        db.refresh(doctor_notification)

        background_tasks.add_task(
            manager.send_to_user,
            doctor.user_id,
            {
                "type": "notification",
                "id": doctor_notification.id,
                "title": doctor_notification.title,
                "message": doctor_notification.message,
                "appointment_id": appointment.id,
            },
        )

    return appointment
