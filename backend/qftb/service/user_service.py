import sqlalchemy.exc
from fastapi import Depends, HTTPException, status
from psycopg2.errors import UniqueViolation
from sqlalchemy import select
from sqlalchemy.orm import Session

from qftb.database import get_db
from qftb.models import User
from qftb.schemas import CreateUser, Message
from qftb.util.password import hash


class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_all_users(self) -> list[User]:
        try:
            users = self.db.execute(select(User)).scalars().all()
            return list(users)
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            ) from err

    def get_single_user(self, user_id: int) -> User:
        try:
            user = self.db.execute(select(User).where(User.id == user_id)).scalar_one()
            return user
        except sqlalchemy.exc.NoResultFound as err:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found",
            ) from err

    def create_user(self, user_payload: CreateUser) -> Message | None:
        try:
            user_insert = User(
                first_name=user_payload.first_name.lower(),
                last_name=user_payload.last_name.lower(),
                email=user_payload.email.lower(),
                hashed_password=hash(user_payload.password),
            )
            self.db.add(user_insert)
            self.db.commit()
            self.db.refresh(user_insert)
            return Message(detail="User created successfully")
        except sqlalchemy.exc.IntegrityError as err:
            if isinstance(err.orig, UniqueViolation):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="User already exists"
                ) from err
        except Exception as err:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            ) from err
