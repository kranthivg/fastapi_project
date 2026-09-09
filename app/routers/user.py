from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas, utils
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=201, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(email=str(user.email).lower(), password=utils.hash(user.password))
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Email already registered") from None
    db.refresh(new_user)
    return new_user


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(oauth2.get_current_user)):
    return user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, user: models.User = Depends(oauth2.get_current_user)):
    if id != user.id:
        raise HTTPException(403, "You can only view your own account")
    return user
