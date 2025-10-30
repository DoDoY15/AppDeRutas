from pydantic import BaseModel
from typing import Optional
from datetime import date 

class PointOfStopBase(BaseModel):
    name: str
    latitude: float
    longitude: float

    external_id: Optional[str] = None
    chain: Optional[str] = None
    Segment: Optional[str] = None
    channel: Optional[str] = None
    Region: Optional[str] = None
    Country: Optional[str] = None
    City: Optional[str] = None
    Address: Optional[str] = None
    WorkingStatus: Optional[bool] = True
    visits_per_week: Optional[int] = 1
    visit_duration_seconds: Optional[int] = 1800 
    priority: Optional[int] = 1
    last_visited_at: Optional[date] = None 
    class Config:
        from_attributes = True
        extra = 'ignore' 

class PointOfStopCreate(PointOfStopBase):
    pass 

class PointOfStop(PointOfStopBase):
    id: int
    
    class Config:
        orm_mode = True 
        from_attributes = True 
