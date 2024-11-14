from datetime import UTC, datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .. import models
from ..config import settings
from ..database import get_db
from ..schemas import JwtInfo, UserInfo
from ..util.password import verify_password


def auth_user(username: str, password: str, db: Session = Depends(get_db)) -> UserInfo:
    """
    Authenitcate User

    DB query for user.
    1. If present and password matches return username.
    2. Check user refresh limit - if more than 1 minute since last access reset
    3. Delete all previous rotated refresh tokens.

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

    user_info = UserInfo(id=user.id, username=user.email)
    current_time = datetime.now(UTC)
    # convert to timezone aware
    last_accessed = user.last_accessed.replace(tzinfo=timezone.utc)
    try:
        if current_time - last_accessed > timedelta(minutes=1):
            user.refresh_limit = 1
            print(f"Reset user {username} refresh limit")
        user.last_accessed = current_time
        db.commit()
        refresh_token_cleanup(user_info, db)
        return user_info
    except Exception as err:
        db.rollback()
        raise err


def generate_access_token(user_info: UserInfo, expires_delta: timedelta) -> str:
    """
    Generate JWT access token

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


def generate_refresh_token(
    user_info: UserInfo, expires_delta: timedelta, db: Session = Depends(get_db)
) -> str:
    """
    Generate JWT refresh token
    1. Encode refresh with username, exp and id
    2. Store refresh token in the refresh_tokens table.
    3. Return JWT

    Parameters:
    - username: string
    - expires_delta: timedelta
    - db: Session

    Returns:
    - JWT: String
    """
    encode = {"sub": user_info.username, "id": user_info.id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    refresh_token = jwt.encode(encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGO)
    try:
        token = models.RefreshToken(
            user_id=user_info.id,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=1),
            revoked=False,
        )
        db.add(token)
        db.commit()
        db.refresh(token)
        return refresh_token
    except Exception as err:
        db.rollback()
        print(f"Refresh token creation failed.. {err}")
        raise err


def decode_token(authorization: str) -> JwtInfo:
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
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGO])
        return JwtInfo(id=decoded["id"], sub=decoded["sub"], exp=decoded["exp"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


def invalidate_refresh_token(
    decoded_token: JwtInfo, refresh_token: str, db: Session = Depends(get_db)
) -> None:
    try:
        token = (
            db.query(models.RefreshToken)
            .filter(
                models.RefreshToken.refresh_token == refresh_token,
                models.RefreshToken.user_id == decoded_token.id,
            )
            .first()
        )

        if not token:
            raise HTTPException(detail="Token Not found", status_code=404)

        if token.revoked is True:
            print("Token already revoked")
            raise HTTPException(detail="Token already revoked", status_code=401)
        else:
            token.revoked = True
            # Do I need an if statement here?? if token is revoked or not
            db.commit()
            print("Refresh token invalidated successfully")
    except Exception as err:
        db.rollback()
        print("Something went wrong with token Invaldation")
        raise err


def validate_refresh_session(
    decoded_token: JwtInfo, refresh_token: str, db: Session = Depends(get_db)
) -> UserInfo:
    if decoded_token.exp is not None and datetime.now(timezone.utc) > decoded_token.exp:
        invalidate_refresh_token(decoded_token, refresh_token, db)
        raise HTTPException(detail="refresh token is expired", status_code=401)
    else:
        invalidate_refresh_token(decoded_token, refresh_token, db)
    try:
        user = db.query(models.User).filter(models.User.id == decoded_token.id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

        current_time = datetime.now(UTC)
        last_accessed = user.last_accessed.replace(tzinfo=timezone.utc)
        if current_time - last_accessed < timedelta(minutes=1):
            print("User refresh limit", user.refresh_limit)
            user.refresh_limit += 1
            if user.refresh_limit > 3:
                # TODO: do we revoke this token ???
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
        else:
            # Reset count and update timestamp
            user.refresh_limit = 1
            print("User refresh limit reset", user.refresh_limit)
            user.last_accessed = current_time

        # Step 5: Commit rate limit tracking updates
        user.last_accessed = current_time
        db.commit()

        return UserInfo(id=user.id, username=user.email)
    except HTTPException as http_err:
        # Reraise known HTTP exceptions (like 401, 404, or 429) without modification
        raise http_err
    except Exception as err:
        db.rollback()
        print(err)
        raise HTTPException(status_code=500, detail="Internal server error") from err


def refresh_token_cleanup(user_info: UserInfo, db: Session = Depends(get_db)) -> None:
    try:
        db.query(models.RefreshToken).filter(models.RefreshToken.user_id == user_info.id).delete()
        db.commit()
        print(f"Token clean up for user {user_info.username}")
    except Exception as err:
        db.rollback()
        raise err


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
