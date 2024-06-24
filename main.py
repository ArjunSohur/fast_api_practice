from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Annotated

import models
from sqlalchemy.orm import Session
from database import SessionLocal, engine
 
app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class user(BaseModel):
    user_id: int
    name: str
    email: str
    is_active: bool

class userIntrests(BaseModel):
    user_id: int
    intrests: str

# Dependency to get the session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency with annotation for type hinting
db_dependency = Depends(get_db)


@app.post("/users/", response_model=user)
async def create_user(user: user, db: Session = db_dependency):
    db_user = models.User(id=user.user_id, name=user.name, email=user.email, is_active=user.is_active)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user