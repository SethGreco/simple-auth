from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import Message, Token
from ..service.auth import (
    auth_user,
    decode_token,
    generate_access_token,
    generate_refresh_token,
    invalidate_refresh_token,
    restrict_ip_address,
    validate_refresh_session,
)

router = APIRouter(
    prefix="/login",
    tags=["Login"],
    responses={status.HTTP_401_UNAUTHORIZED: {"model": Message}},
)


security = HTTPBasic()


@router.post("/user/", response_model=Token, status_code=status.HTTP_200_OK)
def login_user(
    response: Response,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Token:
    """
    Login user client

    Parameters:
    - credentials: Basic Auth credentials
    - db: The database session dependency.

    Returns:
    - Token
    """

    user_info = auth_user(credentials.username, credentials.password, db)
    access_token = generate_access_token(user_info, timedelta(minutes=15))
    refresh_token = generate_refresh_token(user_info, timedelta(days=1), db)
    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24,
        expires=60 * 60 * 24,
    )
    print("Refresh token created")
    return Token(access_token=access_token, token_type="bearer")


@router.post("/admin/", status_code=status.HTTP_200_OK)
def login_admin(
    ip=Depends(restrict_ip_address),
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Login admin client

    Parameters:
    - credentials: Basic Auth credentials
    - db: The database session dependency.

    Returns:
    - Bool
    """
    return True


# I will need to check that user in the database to invalidate their refresh token
# then generate a new access and refresh, store refresh in db and return response.
@router.get("/refresh")
def user_valid_check(
    response: Response,
    refreshToken: Annotated[str | None, Cookie()] = None,
    db: Session = Depends(get_db),
) -> Token:
    if refreshToken is None:
        raise HTTPException(status_code=401, detail="unauthenticated")
    decoded_token = decode_token(refreshToken)
    user_info = validate_refresh_session(decoded_token, refreshToken, db)
    access_token = generate_access_token(user_info, timedelta(minutes=15))
    refresh_token = generate_refresh_token(user_info, timedelta(days=1), db)
    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24,
        expires=60 * 60 * 24,
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/logout")
def invalidate_refresh(
    refreshToken: Annotated[str, Cookie()], db: Session = Depends(get_db)
) -> Message:
    decoded_token = decode_token(refreshToken)
    invalidate_refresh_token(decoded_token, refreshToken, db)
    return Message(detail="User tokens revoked")
