import secrets
from datetime import UTC, datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import delete, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from qftb.config import settings
from qftb.database import get_db
from qftb.models import RefreshToken, User
from qftb.schemas import JwtInfo, UserInfo
from qftb.util.password import verify_password


class AuthenticationManager:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def authenticate_user(self, username: str, password: str) -> UserInfo:
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
        - UserInfo
        """
        res = self.db.execute(select(User).where(User.email == username))
        try:
            user = res.scalar_one()
        except NoResultFound:
            print("User not found")
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
            self.db.commit()
            self.refresh_token_cleanup(user_info)
            return user_info
        except Exception as err:
            self.db.rollback()
            print(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error"
            )

    def generate_access_token(self, user_info: UserInfo, expires_delta: timedelta) -> str:
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

    def generate_refresh_token(self, user_id: int) -> str:
        """
        1. Generate opaque refresh token
        2. Store refresh token in the refresh_tokens table.
        3. Return refresh_token

        Parameters:
        - user_id: int
        - db: Session

        Returns:
        - : String
        """
        refresh_token = secrets.token_urlsafe(40)
        try:
            token = RefreshToken(
                user_id=user_id,
                refresh_token=refresh_token,
                expires_at=datetime.utcnow() + timedelta(days=1),
                revoked=False,
            )
            self.db.add(token)
            self.db.commit()
            self.db.refresh(token)
            return refresh_token
        except Exception as err:
            self.db.rollback()
            print(f"Refresh token creation failed.. {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Service Error"
            )

    def decode_token(self, authorization: str) -> JwtInfo:
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

    def invalidate_refresh_token(self, refresh_token: str) -> int:
        try:
            res = self.db.execute(
                select(RefreshToken).where(RefreshToken.refresh_token == refresh_token)
            )
            token = res.scalar_one()

            if token.revoked is True:
                print("Token already revoked")
                raise HTTPException(
                    detail="Token already revoked", status_code=status.HTTP_401_UNAUTHORIZED
                )

            token.revoked = True
            self.db.commit()

            last_accessed = token.expires_at.replace(tzinfo=timezone.utc)
            if last_accessed < datetime.now(timezone.utc):
                raise HTTPException(detail="refresh token is expired", status_code=401)
            print("Refresh token invalidated successfully")
            return token.user_id
        except NoResultFound:
            raise HTTPException(detail="Token Not found", status_code=status.HTTP_404_NOT_FOUND)
        except Exception as err:
            self.db.rollback()
            print(f"Something went wrong with token Invaldation {err}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error"
            )

    def validate_refresh_session(self, refresh_token: str) -> UserInfo:
        refresh_user = self.invalidate_refresh_token(refresh_token)
        try:
            res = self.db.execute(select(User).where(User.id == refresh_user))
            user = res.scalar_one()

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
            self.db.commit()

            return UserInfo(id=user.id, username=user.email)
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
        except HTTPException as http_err:
            # Reraise known HTTP exceptions (like 401, 404, or 429) without modification
            raise http_err
        except Exception as err:
            self.db.rollback()
            print(err)
            raise HTTPException(status_code=500, detail="Internal server error") from err

    def refresh_token_cleanup(self, user_info: UserInfo) -> None:
        try:
            self.db.execute(delete(RefreshToken).where(RefreshToken.user_id == user_info.id))
            self.db.commit()
            print(f"Token clean up for user {user_info.username}")
        except Exception as err:
            self.db.rollback()
            print(err)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error"
            )

    def restrict_ip_address(self, req: Request) -> str:
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
