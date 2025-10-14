from pydantic import BaseModel
from typing import Optional
from datetime import date
from .models import UserRole

# Schema base para um Ponto de Parada
class PointOfStopBase(BaseModel):
    
    id: int 
    name: str
    latitude: float
    longitude: float
    Segment: Optional[str] = None
    country: Optional[str] = None
    City: Optional[str] = None
    Region: Optional[str] = None
    Address: Optional[str] = None
    WorkingStatus: bool 
    visits_per_week: int 
    visit_duration_hours: int 
    last_visited_at : Optional[date] 
    visits: Optional[list] 
    
class PointOfStopCreate(PointOfStopBase):
    pass

class PointOfStop(PointOfStopBase):
    id: int
    last_visited_at: Optional[date] = None
    class Config:
        from_atributes = True

# Schemas de User (permanecem os mesmos)
class UserBase(BaseModel):
    username: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    class Config:
        from_atributes = True