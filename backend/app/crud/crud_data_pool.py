from sqlalchemy.orm import Session
from typing import List, Tuple
from app.db.models import PointOfStop, User, UserRole

def get_data_pool(db: Session) -> Tuple[List[User], List[PointOfStop]]:

    workers = db.query(User).filter(
        User.role == UserRole.USER, 
        User.working_status == True
    ).all()

    pdv_pool = db.query(PointOfStop).filter(
        PointOfStop.visits_per_week > 0,
        PointOfStop.working_status == True 
    ).all()

    return workers, pdv_pool