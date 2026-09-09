from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.database.models.user import UserRole

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role: Optional[UserRole] = UserRole.CITIZEN

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    role: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True
