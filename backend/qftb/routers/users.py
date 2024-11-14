from typing import Annotated

import sqlalchemy.exc
from fastapi import APIRouter, Depends, Header, HTTPException, status
from psycopg2.errors import UniqueViolation
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import CreateUser, ErrorResponse, Message, UserResponse
from ..service.auth import decode_token
from ..util.password import hash

router = APIRouter(prefix="/user", tags=["User"])


@router.get(
    "/",
    response_model=list[UserResponse],
    summary="Retrieve all users",
    description="Non-sensitive view of user details",
)
def read_users_non_admin(db: Session = Depends(get_db)):
    """
    Get all users

    Returns a list of user objects containing non sensetive user data.
    If no users are found, an empty list is returned.

    Parameters:
    - db: The database session dependency.

    Returns:
    - List[schemas.UserResponse]: A list of user objects containing user details.
    """
    try:
        users = db.query(models.User).all()
        return users
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from err


@router.get(
    "/{id}/",
    response_model=UserResponse,
    summary="Retrieve single user",
    description="",
    responses={404: {"model": Message}},
)
def read_single_user_non_admin(
    id: int,
    authorization: Annotated[str, Header()],
    db: Session = Depends(get_db),
):
    """
    Get single user by ID

    Returns a single user object containing non sensetive user data.

    Parameters:
    - db: The database session dependency.

    Returns:
    - schemas.UserResponse: A user object containing user details

    """
    validated = decode_token(authorization)
    try:
        user = db.query(models.User).filter(models.User.id == id).one()
        return user
    except sqlalchemy.exc.NoResultFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        ) from err


@router.post(
    "/",
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"model": Message},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        409: {"model": Message},
    },
)
def create_single_user(user_payload: CreateUser, db: Session = Depends(get_db)) -> Message | None:
    """
    POST create a single user

    Parameters:
    - user_payload: CreateUser model.
    - db: The database session dependency.

    Returns:
    - {}: A user object containing success msg.
    """
    try:
        user_insert = models.User(
            first_name=user_payload.first_name,
            last_name=user_payload.last_name,
            email=user_payload.email,
            hashed_password=hash(user_payload.password),
        )
        db.add(user_insert)
        db.commit()
        db.refresh(user_insert)
        return Message(detail="User created successfully")
    except sqlalchemy.exc.IntegrityError as err:
        if isinstance(err.orig, UniqueViolation):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            ) from err
    except Exception as err:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        ) from err
