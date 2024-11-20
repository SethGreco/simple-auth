from typing import Annotated

from fastapi import APIRouter, Depends, Header, status

from qftb.schemas import CreateUser, ErrorResponse, Message, UserResponse
from qftb.service.auth_service import AuthenticationManager
from qftb.service.user_service import UserService

router = APIRouter(prefix="/user", tags=["User"])


@router.get(
    "",
    response_model=list[UserResponse],
    summary="Retrieve all users",
    description="Non-sensitive view of user details",
)
def read_users_non_admin(user_service: UserService = Depends(UserService)):
    """
    Get all users

    Returns a list of user objects containing non sensetive user data.
    If no users are found, an empty list is returned.

    Parameters:
    - user_service: UserService class.

    Returns:
    - List[schemas.UserResponse]: A list of user objects containing user details.
    """
    return user_service.get_all_users()


@router.get(
    "/{id}",
    response_model=UserResponse,
    summary="Retrieve single user",
    description="",
    responses={404: {"model": Message}},
)
def read_single_user_non_admin(
    id: int,
    authorization: Annotated[str, Header()],
    auth_manager: AuthenticationManager = Depends(AuthenticationManager),
    user_service: UserService = Depends(UserService),
) -> UserResponse:
    """
    Get single user by ID

    Returns a single user object containing non sensetive user data.

    Parameters:
    - db: The database session dependency.

    Returns:
    - schemas.UserResponse: A user object containing user details

    """
    validated = auth_manager.decode_token(authorization)
    return user_service.get_single_user(id)


@router.post(
    "",
    response_model=Message,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"model": Message},
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        409: {"model": Message},
    },
)
def create_single_user(
    user_payload: CreateUser, user_service: UserService = Depends(UserService)
) -> Message | None:
    """
    POST create a single user

    Parameters:
    - user_payload: CreateUser model.
    - db: The database session dependency.

    Returns:
    - {}: A user object containing success msg.
    """
    return user_service.create_user(user_payload)
