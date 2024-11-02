from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import Message, Token
from ..service.auth import auth_user, generate_token, restrict_ip_address, validate_token

router = APIRouter(
    prefix="/login",
    tags=["Login"],
    responses={status.HTTP_401_UNAUTHORIZED: {"model": Message}},
)


security = HTTPBasic()


@router.post("/user/", response_model=Token, status_code=status.HTTP_200_OK)
def login_user(
    credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)
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
    token = generate_token(user_info, timedelta(minutes=1))
    return Token(access_token=token, token_type="bearer")


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


@router.get("/valid/")
def user_valid_check(authorization: Annotated[str | None, Header()] = None):
    validate_token(authorization)
    return True
