from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .routers import auth, post, user, vote

app = FastAPI(
    title="FastAPI Studio — Social API",
    version="2.0.0",
    description="Accounts, posts and voting. Drafts are visible only to their author.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
for router in (post.router, user.router, auth.router, vote.router):
    app.include_router(router)


@app.get("/")
def root():
    return {"message": "FastAPI Studio", "version": "2.0.0", "docs": "/docs"}


@app.get("/health", tags=["System"])
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        raise HTTPException(503, "Database unavailable") from None
    return {"status": "ok", "runtime": "FastAPI", "version": "2.0.0"}
