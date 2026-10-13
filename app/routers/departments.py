
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.department import Department
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)
from app.auth.dependencies import require_roles

router = APIRouter(prefix="/departments", tags=["Departments"])


@router.post("/", response_model=DepartmentResponse, status_code=201)
def create_department(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    existing = db.query(Department).filter(
        Department.name == data.name
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Department already exists")

    department = Department(
        name=data.name,
        description=data.description,
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.get("/", response_model=list[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).order_by(Department.name).all()


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db)):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    return department


@router.patch("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: int,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    updates = data.model_dump(exclude_unset=True)

    if "name" in updates and updates["name"] is not None:
        duplicate = db.query(Department).filter(
            Department.name == updates["name"],
            Department.id != department_id,
        ).first()

        if duplicate:
            raise HTTPException(
                status_code=409,
                detail="Department name already exists",
            )

    for key, value in updates.items():
        setattr(department, key, value)

    db.commit()
    db.refresh(department)
    return department


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("Admin")),
):
    department = db.query(Department).filter(
        Department.id == department_id
    ).first()

    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    if department.doctors:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete a department with assigned doctors",
        )

    db.delete(department)
    db.commit()
    return None
