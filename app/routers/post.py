from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import exists, func, or_, select
from sqlalchemy.orm import Session

from .. import models, oauth2, schemas
from ..database import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


def query_posts(user):
    votes = (
        select(func.count())
        .where(models.Vote.post_id == models.Post.id)
        .correlate(models.Post)
        .scalar_subquery()
    )
    voted = exists().where(models.Vote.post_id == models.Post.id, models.Vote.user_id == user.id)
    return select(models.Post, votes, voted).where(
        or_(models.Post.published.is_(True), models.Post.owner_id == user.id)
    )


def out(row):
    return {"Post": row[0], "votes": row[1], "voted": row[2]}


@router.get("/", response_model=list[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    user: models.User = Depends(oauth2.get_current_user),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    search: str = Query("", max_length=200),
    mine: bool = False,
):
    stmt = query_posts(user).where(models.Post.title.contains(search, autoescape=True))
    if mine:
        stmt = stmt.where(models.Post.owner_id == user.id)
    return [out(r) for r in db.execute(stmt.order_by(models.Post.id.desc()).offset(skip).limit(limit)).all()]


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), user: models.User = Depends(oauth2.get_current_user)):
    row = db.execute(query_posts(user).where(models.Post.id == id)).first()
    if row is None:
        raise HTTPException(404, "Post not found")
    return out(row)


@router.post("/", status_code=201, response_model=schemas.Post)
def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(oauth2.get_current_user),
):
    item = models.Post(owner_id=user.id, **post.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def owned(id, db, user):
    post = db.get(models.Post, id)
    if not post:
        raise HTTPException(404, "Post not found")
    if post.owner_id != user.id:
        raise HTTPException(403, "Only the author can change this post")
    return post


@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(oauth2.get_current_user),
):
    item = owned(id, db, user)
    for key, value in post.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{id}", status_code=204)
def delete_post(id: int, db: Session = Depends(get_db), user: models.User = Depends(oauth2.get_current_user)):
    db.delete(owned(id, db, user))
    db.commit()
    return Response(status_code=204)
