
import hashlib
import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, ALGORITHM
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.token import Token

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token_record = db.query(RefreshToken).filter(
        RefreshToken.token_hash == hash_token(refresh_token),
        RefreshToken.is_revoked.is_(False),
    ).first()

    if not token_record:
        raise HTTPException(status_code=401, detail="Refresh token revoked or unknown")

    if token_record.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
        token_record.is_revoked = True
        db.commit()
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = db.query(User).filter(
        User.id == int(user_id),
        User.is_active.is_(True),
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )

    return Token(access_token=access_token)


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.is_revoked.is_(False),
    ).all()

    for token in tokens:
        token.is_revoked = True

    db.commit()
    return {"message": "Logged out successfully"}
