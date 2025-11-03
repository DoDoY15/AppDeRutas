from pydantic import BaseModel
from typing import Optional
from datetime import date 

class PointOfStopBase(BaseModel):

    name: str
    latitude: float
    longitude: float
    external_id: str 
    
    chain: Optional[str] = None
    segment: Optional[str] = None
    channel: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    working_status: Optional[bool] = True
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
         
        from_attributes = True 
