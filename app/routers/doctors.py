
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.department import Department
from app.schemas.doctor import (
    DoctorCreate,
    DoctorUpdate,
    DoctorResponse,
)
from app.auth.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("/", response_model=DoctorResponse, status_code=201)
def create_doctor(
    data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role != "Doctor":
        raise HTTPException(
            status_code=400,
            detail="The selected user must have the Doctor role",
        )

    if db.query(Doctor).filter(Doctor.user_id == data.user_id).first():
        raise HTTPException(
            status_code=409,
            detail="Doctor profile already exists for this user",
        )

    department = db.query(Department).filter(
        Department.id == data.department_id
    ).first()
    if not department or not department.is_active:
        raise HTTPException(
            status_code=404,
            detail="Active department not found",
        )

    doctor = Doctor(**data.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("/", response_model=list[DoctorResponse])
def list_doctors(
    department_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Doctor).filter(Doctor.is_active.is_(True))

    if department_id is not None:
        query = query.filter(Doctor.department_id == department_id)

    return query.order_by(Doctor.id).all()


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(
        Doctor.id == doctor_id,
        Doctor.is_active.is_(True),
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return doctor


@router.patch("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    doctor_id: int,
    data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    updates = data.model_dump(exclude_unset=True)

    if updates.get("department_id") is not None:
        department = db.query(Department).filter(
            Department.id == updates["department_id"],
            Department.is_active.is_(True),
        ).first()
        if not department:
            raise HTTPException(
                status_code=404,
                detail="Active department not found",
            )

    for key, value in updates.items():
        setattr(doctor, key, value)

    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("/me/profile", response_model=DoctorResponse)
def get_my_doctor_profile(
    current_user: User = Depends(require_roles("Doctor")),
    db: Session = Depends(get_db),
):
    doctor = db.query(Doctor).filter(
        Doctor.user_id == current_user.id
    ).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    return doctor
