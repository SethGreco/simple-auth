from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import (
    OAuth2PasswordRequestForm,
)

from qftb.schemas import Message, Token
from qftb.service.auth_service import AuthenticationManager

router = APIRouter(
    prefix="/login",
    tags=["Login"],
    responses={status.HTTP_401_UNAUTHORIZED: {"model": Message}},
)


@router.post("/user/", response_model=Token, status_code=status.HTTP_200_OK)
def login_user(
    response: Response,
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_manager: AuthenticationManager = Depends(AuthenticationManager),
) -> Token:
    """
    Login user client

    Parameters:
    - credentials: Basic Auth credentials
    - db: The database session dependency.

    Returns:
    - Token
    """

    user_info = auth_manager.authenticate_user(credentials.username, credentials.password)
    access_token = auth_manager.generate_access_token(user_info, timedelta(minutes=15))
    refresh_token = auth_manager.generate_refresh_token(user_info.id)
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
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_manager: AuthenticationManager = Depends(AuthenticationManager),
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


@router.get("/refresh")
def user_valid_check(
    response: Response,
    refreshToken: Annotated[str | None, Cookie()] = None,
    auth_manager: AuthenticationManager = Depends(AuthenticationManager),
) -> Token:
    if refreshToken is None:
        raise HTTPException(status_code=401, detail="unauthenticated")
    user_info = auth_manager.validate_refresh_session(refreshToken)
    access_token = auth_manager.generate_access_token(user_info, timedelta(minutes=15))
    refresh_token = auth_manager.generate_refresh_token(user_info.id)
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
    refreshToken: Annotated[str, Cookie()],
    auth_manager: AuthenticationManager = Depends(AuthenticationManager),
) -> Message:
    refresh_user = auth_manager.invalidate_refresh_token(refreshToken)
    return Message(detail=f"User ${refresh_user} token revoked")
