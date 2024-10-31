from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..schemas import AdminUserView

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users/", response_model=list[AdminUserView])
def admin_read_users(db: Session = Depends(get_db)):
    """
    GET all users - for ADMIN view
    """
    users = db.query(models.User)
    return users
