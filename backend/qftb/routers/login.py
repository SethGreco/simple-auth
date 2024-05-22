from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import APIRouter, Depends, status
from qftb.schemas import Message, Token
from qftb.database import get_db
from qftb.service.auth import auth_user, generate_token, restrict_ip_address
from sqlalchemy.orm import Session
from datetime import timedelta


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
    token = generate_token(user_info, timedelta(minutes=20))
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
