from sqlalchemy import Boolean, Column, Integer, String, Float, Date, Enum, ForeignKey ,DateTime , func
from sqlalchemy.orm import relationship
import enum
from .database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class VisitStatus(str, enum.Enum):

    PENDING = "Pendente"
    VISITED = "Concluída"
    NOT_VISITED = "Não visitada"

class User(Base):
    __tablename__ = "users"
    external_id = Column(String, unique=True, index=True, nullable=True)    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True) 
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    visits = relationship("DailyVisit", back_populates="user")
    start_latitude = Column(Float, nullable=True)
    start_longitude = Column(Float, nullable=True)
    weakly_working_seconds = Column(Float , nullable=False , default=28800)
    daily_work_duration_seconds= Column(Integer, nullable=True)
    max_visits_per_day = Column(Integer, nullable=True)
    full_name = Column(String, nullable=True , index=True)
    WorkingStatus = Boolean

class PointOfStop(Base):
    
    # identificacion 

    __tablename__ = "point_of_stops"
    external_id = Column(String, unique=True, index=True, nullable=True)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    chain = Column(String, nullable=True)
    Segment = Column(String, nullable=True)
    channel = Column(String, nullable=True)

    # localizacion

    City = Column(String, nullable=True)
    Country = Column(String, nullable=True)
    Region = Column(String, nullable=True)
    Address = Column(String, nullable=True) 
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Variables

    WorkingStatus = Column(Boolean, nullable=True)
    visits_per_week = Column(Integer, default=1)
    visit_duration_seconds = Column(Integer, default=1) 
    priority = Column(Integer, default=1)
    last_visited_at = Column(Date, nullable=True)
    visits = relationship("DailyVisit", back_populates="point_of_stop")

class DailyVisit(Base):
    __tablename__ = "daily_visits"
    id = Column(Integer, primary_key=True, index=True)
    visit_date = Column(Date, nullable=False, index=True)
    status = Column(Enum(VisitStatus), default=VisitStatus.PENDING)
    user_id = Column(Integer, ForeignKey("users.id"))

    point_of_stop_id = Column(Integer, ForeignKey("point_of_stops.id"))

    user = relationship("User", back_populates="visits")
    point_of_stop = relationship("PointOfStop", back_populates="visits")

    optimization_run_id = Column(Integer, ForeignKey("optimization_runs.id"), nullable=True)
    optimization_run = relationship("OptimizationRun", back_populates="daily_visits")

class DistanceCache(Base):
    __tablename__ = "distance_cache"
    id = Column(Integer, primary_key=True, index=True)
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lng = Column(Float, nullable=False)
    distance_meters = Column(Integer)
    duration_seconds = Column(Integer)

class weaklyPlan(Base):
    __tablename__ = "weekly_plans"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")
    optimization_run_id = Column(Integer, ForeignKey("optimization_runs.id"), nullable=True)
    optimization_run = relationship("OptimizationRun", back_populates="weekly_plans")
    total_pdvs_assigned = Column(Integer, default=0)

class OptimizationStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class OptimizationRun(Base):
    __tablename__ = "optimization_runs"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(OptimizationStatus), default=OptimizationStatus.PENDING)

    total_pdvs_assigned = Column(Integer, default=0)
    total_pdvs_unassigned = Column(Integer, default=0)

    daily_visits = relationship("DailyVisit", back_populates="optimization_run")
    weekly_plans = relationship("weaklyPlan", back_populates="optimization_run")