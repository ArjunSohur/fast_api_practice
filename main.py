from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, engine
from sqlalchemy import Sequence
from models import Base, User, UserInterests

import models
from sqlalchemy.orm import Session
from database import SessionLocal, engine
 
app = FastAPI()

sequence = Sequence('users_user_id_seq')
sequence.create(engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

models.Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    is_active: bool = True

class UserResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

class UserInterestsCreate(BaseModel):
    user_id: int
    interests: str

class UserInterestsResponse(BaseModel):
    id: int
    user_id: int
    interests: str

    class Config:
        from_attributes = True

# Dependency to get the session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency with annotation for type hinting
db_dependency = Depends(get_db)

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = User(name=user.name, email=user.email, is_active=user.is_active)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database integrity error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

# Endpoint to handle user interests
@app.post("/user_interests/", response_model=UserInterestsResponse)
async def create_user_interests(user_interests: UserInterestsCreate, db: Session = Depends(get_db)):
    db_interests = UserInterests(user_id=user_interests.user_id, interests=user_interests.interests)
    db.add(db_interests)
    db.commit()
    db.refresh(db_interests)
    return db_interests