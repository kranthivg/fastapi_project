from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/vote", tags=["Votes"])


@router.post("/", status_code=201)
def vote(
    vote: schemas.Vote, db: Session = Depends(get_db), user: models.User = Depends(oauth2.get_current_user)
):
    post = db.get(models.Post, vote.post_id)
    if not post or (not post.published and post.owner_id != user.id):
        raise HTTPException(404, "Post not found")
    key = {"user_id": user.id, "post_id": vote.post_id}
    found = db.get(models.Vote, key)
    if vote.dir == 1:
        if found:
            raise HTTPException(409, "Already voted")
        db.add(models.Vote(**key))
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise HTTPException(409, "Already voted") from None
        return {"message": "Successfully added vote"}
    if not found:
        raise HTTPException(404, "Vote does not exist")
    db.delete(found)
    db.commit()
    return {"message": "Successfully deleted vote"}
