from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.db.models import WeeklyPlan

class WeeklyPlanBase(BaseModel):
    
    user_id: int
    optimization_run_id: Optional[int] = None
    

    class Config:
        from_attributes = True
        extra = 'ignore'

class WeeklyPlanCreate(WeeklyPlan):

    pass

class WeeklyPlan(WeeklyPlan):

    id: int

    class Config:
        orm_mode = True 
        from_attributes = True