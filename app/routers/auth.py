from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas, utils
from ..database import get_db

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == credentials.username.strip().lower()))
    valid, updated = utils.pwd_context.verify_and_update(
        credentials.password, user.password if user else utils.DUMMY_HASH
    )
    if not user or not valid:
        raise HTTPException(401, "Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    if updated:
        user.password = updated
        db.commit()
    return {"access_token": oauth2.create_access_token({"user_id": user.id}), "token_type": "bearer"}
