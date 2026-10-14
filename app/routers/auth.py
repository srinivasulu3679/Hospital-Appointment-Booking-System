import hashlib
from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered",
        )

    if user_data.phone:
        existing_phone = db.query(User).filter(
            User.phone == user_data.phone
        ).first()

        if existing_phone:
            raise HTTPException(
                status_code=409,
                detail="Phone number is already registered",
            )

    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        hashed_password=hash_password(user_data.password),
        role="Patient",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if (
        not user
        or not verify_password(form_data.password, user.hashed_password)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    refresh_token, expires_at = create_refresh_token(user.id)

    expires_at_db = expires_at.astimezone(timezone.utc).replace(
        tzinfo=None
    )

    refresh_token_record = RefreshToken(
        user_id=user.id,
        token_hash=hashlib.sha256(
            refresh_token.encode("utf-8")
        ).hexdigest(),
        expires_at=expires_at_db,
        is_revoked=False,
    )

    db.add(refresh_token_record)
    db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user