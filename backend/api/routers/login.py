from datetime import timedelta
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from fastapi import APIRouter, Depends, status

from api.schemas import Token
from api.database import get_db
from api.service.auth import auth_user, generate_token, restrict_ip_address

from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/login",
    tags=["Login"],
    responses={
        status.HTTP_200_OK: {"description": "Sucessful"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    },
)


security = HTTPBasic()


@router.post("/user/", response_model=Token, status_code=status.HTTP_200_OK)
def login_user(
    credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db)
):
    """
    TODO: move this ??
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
    TODO: move this ??
    """
    return True
