from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.db.models import VisitStatus


class DailyVisitBase(BaseModel):

    visit_date: date
    user_id: int
    point_of_stop_id: int
    status: Optional[VisitStatus] = VisitStatus.PENDING
    optimization_run_id: Optional[int] = None          

    class Config:
        from_attributes = True
        extra = 'ignore'

class DailyVisitCreate(DailyVisitBase):

    pass


class DailyVisit(DailyVisitBase):

    id: int

    class Config:
        from_attributes = True