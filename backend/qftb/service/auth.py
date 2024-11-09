from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from ..database import get_db
from ..schemas import Message
from ..util.password import hash, verify_password


def auth_user(username: str, password: str, db: Session = Depends(get_db)) -> dict:
    """
    Authenitcate User

    DB query for user. If present and password matches return username
    Otherwise throw error.

    Parameters:
    - username: string
    - password: string
    - db: The database session dependency.

    Returns:
    - dict{id,username}
    """
    user = db.query(models.User).filter(models.User.email == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return {"id": user.id, "username": username}


def generate_token(user_info: dict, expires_delta: timedelta) -> str:
    """
    Generate JWT token

    Parameters:
    - username: string
    - expires_delta: timedelta

    Returns:
    - JWT: String
    """
    encode = {"sub": user_info["username"], "id": user_info["id"]}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGO)


def generate_refresh_token(user_info: dict, expires_delta: timedelta) -> str:
    encode = {"id": user_info["id"]}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGO)


def validate_token(authorization: str | None) -> None:
    """
    Validate Token

    Validting token on protected endpoints.

    Parameters:
    - user_info: username and id contained
    - paexpires_delta: timedelta for expired timelimit
    - db: The database session dependency.

    Returns:
    - String
    """
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.replace("Bearer ", "")
    try:
        jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGO])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


def restrict_ip_address(req: Request) -> str:
    """
    ALLOW IPs

    Parameters:
    - req: request info

    Return:
    valid IP address
    """
    client_ip = req.client.host
    if client_ip not in settings.ALLOWED_IP_ADDRESSES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unreachable Host")
    return client_ip


def store_refresh_token(refresh_token: str, user_id: int, db: Session = Depends(get_db)) -> Message:
    try:
        token = models.RefreshToken(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=1),
            created_at=datetime.utcnow(),
            revoked=False,
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return Message(detail="Token Stored")
    except Exception as err:
        print(f"Some err {err}")
        raise


def invalidate_refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    info = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGO])

    print("refresh_token", refresh_token)
    print("user info", info)
    try:
        token = (
            db.query(models.RefreshToken)
            .filter(
                models.RefreshToken.refresh_token == refresh_token,
                models.RefreshToken.user_id == info["id"],
            )
            .first()
        )

        if not token:
            raise HTTPException(detail="Token Not found", status_code=404)

        token.revoked = True
        db.commit()

        return {"message": "Refresh token invalidated successfully"}
    except Exception as err:
        raise


def check_for_valid_refresh(refresh_token: str, user_id: int, db: Session = Depends(get_db)):
    token = (
        db.query(models.RefreshToken)
        .filter(models.RefreshToken.user_id == user_id, models.RefreshToken.revoked == False)
        .first()
    )

    return
