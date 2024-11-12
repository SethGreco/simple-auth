from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from ..database import get_db
from ..schemas import JwtInfo, Message, UserInfo
from ..util.password import verify_password


def auth_user(username: str, password: str, db: Session = Depends(get_db)) -> UserInfo:
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
    return UserInfo(id=user.id, username=user.email)


def generate_token(user_info: UserInfo, expires_delta: timedelta) -> str:
    """
    Generate JWT token

    Parameters:
    - username: string
    - expires_delta: timedelta

    Returns:
    - JWT: String
    """
    encode = {"sub": user_info.username, "id": user_info.id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGO)


def generate_refresh_token(user_info: UserInfo, expires_delta: timedelta) -> str:
    encode = {"sub": user_info.username, "id": user_info.id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGO)


def validate_token(authorization: str) -> JwtInfo:
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
    token = authorization.replace("Bearer ", "")
    print(token)
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGO])
        return JwtInfo(id=decoded["id"], sub=decoded["sub"], exp=decoded["exp"])
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


def invalidate_refresh_token(
    refresh_token: str, info: JwtInfo, db: Session = Depends(get_db)
) -> None:
    if info.exp is not None and datetime.now(timezone.utc) > info.exp:
        raise HTTPException(detail="refresh token is expired", status_code=401)

    try:
        token = (
            db.query(models.RefreshToken)
            .filter(
                models.RefreshToken.refresh_token == refresh_token,
                models.RefreshToken.user_id == info.id,
            )
            .first()
        )

        if not token:
            raise HTTPException(detail="Token Not found", status_code=404)

        token.revoked = True
        db.commit()
        print("Refresh token invalidated successfully")
    except Exception as err:
        print(err)
        raise


def check_for_valid_refresh(
    refresh_token: str, info: JwtInfo, db: Session = Depends(get_db)
) -> UserInfo:
    if info.exp is not None and datetime.now(timezone.utc) > info.exp:
        raise HTTPException(detail="refresh token is expired", status_code=401)

    try:
        token = (
            db.query(models.RefreshToken)
            .filter(
                models.RefreshToken.refresh_token == refresh_token,
                models.RefreshToken.user_id == info.id,
                ~models.RefreshToken.revoked,
            )
            .first()
        )

        if not token:
            raise HTTPException(detail="Token Not found", status_code=404)

        user = db.query(models.User).filter(models.User.id == info.id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        return UserInfo(id=user.id, username=user.email)
    except:
        raise
