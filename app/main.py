from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.auth_tokens import router as auth_tokens_router
from app.routers.departments import router as department_router
from app.routers.doctors import router as doctors_router
from app.routers.doctor_schedules import router as doctor_schedules_router
from app.routers.doctor_leaves import router as doctor_leaves_router
from app.routers.appointments import router as appointments_router
from app.routers.appointment_history import router as appointment_history_router
from app.routers.consultations import router as consultations_router
from app.routers.consultation_files import router as consultation_files_router
from app.routers.prescriptions import router as prescriptions_router
from app.routers.doctor_ratings import router as doctor_ratings_router
from app.routers.notifications import router as notifications_router
from app.routers.audit_logs import router as audit_logs_router
from app.routers.doctor_queue import router as doctor_queue_router
from app.routers.doctor_availability import router as doctor_availability_router
from app.routers.reports import router as reports_router
from app.routers.appointment_reminders import router as appointment_reminders_router
from app.routers.email_logs import router as email_logs_router
from app.routers.websocket_notifications import router as websocket_router

from app.services.scheduler_service import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    try:
        yield
    finally:
        stop_scheduler()


app = FastAPI(
    title="Hospital Appointment Booking System",
    description=(
        "Complete hospital appointment API for patients, doctors, "
        "departments, consultations, prescriptions, and notifications."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", tags=["Health"])
def root():
    return {"message": "Hospital Appointment Booking System API"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(auth_tokens_router)
app.include_router(department_router)
app.include_router(doctors_router)
app.include_router(doctor_schedules_router)
app.include_router(doctor_leaves_router)
app.include_router(appointments_router)
app.include_router(appointment_history_router)
app.include_router(consultations_router)
app.include_router(consultation_files_router)
app.include_router(prescriptions_router)
app.include_router(doctor_ratings_router)
app.include_router(notifications_router)
app.include_router(audit_logs_router)
app.include_router(doctor_queue_router)
app.include_router(doctor_availability_router)
app.include_router(reports_router)
app.include_router(appointment_reminders_router)
app.include_router(email_logs_router)
app.include_router(websocket_router)
