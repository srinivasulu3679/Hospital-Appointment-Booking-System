
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.doctor import Doctor
from app.models.doctor_leave import DoctorLeave
from app.schemas.doctor_leave import DoctorLeaveCreate, DoctorLeaveResponse
from app.auth.dependencies import require_roles

router = APIRouter(prefix="/doctor-leaves", tags=["Doctor Leaves"])


@router.post("/", response_model=DoctorLeaveResponse, status_code=201)
def create_doctor_leave(
    data: DoctorLeaveCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin", "Doctor")),
):
    doctor = db.query(Doctor).filter(
        Doctor.id == data.doctor_id,
        Doctor.is_active.is_(True),
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Active doctor not found")

    if current_user.role == "Doctor" and doctor.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can manage only your own leave",
        )

    if data.start_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Leave start date cannot be in the past",
        )

    leave = DoctorLeave(**data.model_dump())
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return leave


@router.get("/{doctor_id}", response_model=list[DoctorLeaveResponse])
def list_doctor_leaves(
    doctor_id: int,
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return db.query(DoctorLeave).filter(
        DoctorLeave.doctor_id == doctor_id,
        DoctorLeave.end_date >= date.today(),
    ).order_by(DoctorLeave.start_date).all()
