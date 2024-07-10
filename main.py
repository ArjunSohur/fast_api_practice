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

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    user_id: str  # Change to string
    name: str
    email: EmailStr
    is_active: bool = True

class UserResponse(BaseModel):
    id: int
    user_id: str  # Change to string
    name: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True

class UserInterestsCreate(BaseModel):
    id: int
    user_id: str  # Change to string
    interests: str

class UserInterestsResponse(BaseModel):
    id: int
    user_id: str  # Change to string
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

# ---------------------------------------------------------------------------- #
#                                                                              #
# ---------------------------------------------------------------------------- #
# Create and get users                                                         #
# ---------------------------------------------------------------------------- #
#                                                                              #
# ---------------------------------------------------------------------------- #

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = User(user_id=user.user_id, name=user.name, email=user.email, is_active=user.is_active)
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

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user_by_id(num_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == num_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ---------------------------------------------------------------------------- #
#                                                                              #
# ---------------------------------------------------------------------------- #
# Create and get user interests                                                #
# ---------------------------------------------------------------------------- #
#                                                                              #
# ---------------------------------------------------------------------------- #
@app.post("/user_interests/", response_model=UserInterestsResponse)
async def create_user_interests(user_interests: UserInterestsCreate, db: Session = Depends(get_db)):
    # Sanity check
    expected_user_id = read_user_by_id(user_interests.id, db)
    if not expected_user_id:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not expected_user_id.user_id == user_interests.user_id:
        raise HTTPException(status_code=400, detail="User ID does not match ID")

    db_interests = UserInterests(id=user_interests.id,  user_id=user_interests.user_id, interests=user_interests.interests)
    db.add(db_interests)
    db.commit()
    db.refresh(db_interests)
    return db_interests

@app.get("/user_interests/", response_model=List[UserInterestsResponse])
def read_user_interests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    interests = db.query(UserInterests).offset(skip).limit(limit).all()
    return interests

@app.get("/user_interests/{user_id}", response_model=UserInterestsResponse)
def read_user_interests_by_user_id(num_id: str, db: Session = Depends(get_db)):  # Change to str
    user_interests = db.query(UserInterests).filter(UserInterests.id == num_id).first()
    if not user_interests:
        raise HTTPException(status_code=404, detail="User interests not found")
    return user_interests

@app.put("/user_interests/{user_id}", response_model=UserInterestsResponse)
def update_user_interests(num_id: int, user_interests: UserInterestsCreate, db: Session = Depends(get_db)):
    db_user_interests = db.query(UserInterests).filter(UserInterests.id == num_id).first()
    if not db_user_interests:
        raise HTTPException(status_code=404, detail="User interests not found")
    db_user_interests.interests = user_interests.interests
    db.commit()
    db.refresh(db_user_interests)
    return db_user_interests
