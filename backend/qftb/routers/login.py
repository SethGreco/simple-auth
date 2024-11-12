from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import Message, Token
from ..service.auth import (
    auth_user,
    check_for_valid_refresh,
    generate_refresh_token,
    generate_token,
    invalidate_refresh_token,
    restrict_ip_address,
    store_refresh_token,
    validate_token,
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
):
    """
    Login user client

    Parameters:
    - credentials: Basic Auth credentials
    - db: The database session dependency.

    Returns:
    - Token
    """
    user_info = auth_user(credentials.username, credentials.password, db)
    access_token = generate_token(user_info, timedelta(minutes=20))
    refresh_token = generate_refresh_token(user_info, timedelta(days=1))
    res = store_refresh_token(refresh_token, user_info.id, db)
    print(res)
    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60,
        expires=60,
    )
    print(refresh_token)
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
):
    if refreshToken is None:
        raise HTTPException(status_code=401, detail="unauth")

    info = validate_token(refreshToken)
    obj = check_for_valid_refresh(refreshToken, info, db)
    access_token = generate_token(obj, timedelta(minutes=20))
    refresh_token = generate_refresh_token(obj, timedelta(days=1))
    invalidate_refresh_token(refreshToken, info, db)
    res = store_refresh_token(refresh_token, info.id, db)
    print(res)
    response.set_cookie(
        key="refreshToken",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60,
        expires=60,
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/logout")
def invalidate_refresh(refreshToken: Annotated[str, Cookie()], db: Session = Depends(get_db)):
    info = validate_token(refreshToken)
    res = invalidate_refresh_token(refreshToken, info, db)
    return res
