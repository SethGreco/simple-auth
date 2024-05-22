from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from qftb import models
from qftb.config import settings
from qftb.database import get_db
from qftb.util.password import verify_password


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


def validate_token(authorization: str) -> None:
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
