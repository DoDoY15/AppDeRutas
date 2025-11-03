from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.db.models import OptimizationRun


class OptimizationRunBase(BaseModel):
    
    created_at = datetime
    status = enumerate
    total_pdvs_assigned = int

    class Config:
        from_attributes = True
        extra = 'ignore'

class OptimizationRunCreate(OptimizationRun):

    pass

class OptimizationRun(OptimizationRun):

    id: int

    class Config:
        
        from_attributes = True