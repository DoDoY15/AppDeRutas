from pydantic import BaseModel
from typing import Optional
from datetime import date
from models import VisitStatus


class DailyVisitBase(BaseModel):
    """
    Campos comuns que são compartilhados por todos os schemas de DailyVisit.
    """
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
