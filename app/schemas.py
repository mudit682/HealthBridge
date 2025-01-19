# schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_type: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    user_type: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class HospitalCreate(BaseModel):
    name: str
    hospital_type: str
    admin_name: str
    email: str
    contact_number: str
    password_hash: str
    location: str
    latitude: float  # Ensure latitude is included here
    longitude: float
    position: str
    password: str  # If you have password management logic

    class Config:
        orm_mode = True

class HospitalLogin(BaseModel):
    email: EmailStr
    password: str