from pydantic import BaseModel
from typing import Optional
from ..db.models import UserRole 

class UserBase(BaseModel):
    
    username: str 
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = UserRole.USER
    start_latitude: Optional[float] = None
    start_longitude: Optional[float] = None
    daily_work_duration_seconds: Optional[int] = 28800
    max_visits_per_day: Optional[int] = None
    
    class Config:
        from_attributes = True 
        extra = 'ignore'

class UserCreate(UserBase):
    password: str 

class User(UserBase):
    id: int
    
    class Config:
        orm_mode = True
        from_attributes = True
