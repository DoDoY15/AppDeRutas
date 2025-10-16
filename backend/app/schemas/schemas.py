from pydantic import BaseModel
from typing import Optional
from datetime import date
from ..db.models import UserRole

# Schema base para um Ponto de Parada
class PointOfStopBase(BaseModel):
    
    external_id: Optional[int] = None 
    name: str
    chain : Optional[str] = None
    channel: Optional[str] = None
    Segment: Optional[str] = None
    
    latitude: float
    longitude: float
    country: Optional[str] = None
    City: Optional[str] = None
    Region: Optional[str] = None
    Address: Optional[str] = None
    
    WorkingStatus: bool 
    visits_per_week: int 
    visit_duration_hours: int 
    last_visited_at : Optional[date] 
    visits: Optional[list]
    priority: Optional[int] = 1

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