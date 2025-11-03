from sqlalchemy import Boolean, Column, Integer, String, Float, Date, Enum, ForeignKey ,DateTime, UniqueConstraint , func
from sqlalchemy.orm import relationship
import enum
from .database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class VisitStatus(str, enum.Enum):
    PENDING = "Pending"
    VISITED = "Visited"
    NOT_VISITED = "No show"

class User(Base):
    __tablename__ = "users"

    external_id = Column(String, unique=True, index=True, nullable=True) 
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True , index=True)
    email = Column(String, unique=True, index=True) 

    hashed_password = Column(String, nullable=False)

    role = Column(Enum(UserRole), nullable=False)
    start_latitude = Column(Float, nullable=True)
    start_longitude = Column(Float, nullable=True)
    weekly_working_seconds = Column(Float , nullable=False , default=28800)
    daily_work_duration_seconds= Column(Integer, nullable=True)
    max_visits_per_day = Column(Integer, nullable=True)
    
    working_status = Column(Boolean, nullable=True , default= False )


    visits = relationship("DailyVisit", back_populates="user")
    weekly_plans = relationship("WeeklyPlan", back_populates="user")

class PointOfStop(Base):
    # identificacion 
    __tablename__ = "point_of_stops"
    external_id = Column(String, unique=True, index=True, nullable=True)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    chain = Column(String, nullable=True)
    segment = Column(String, nullable=True)
    channel = Column(String, nullable=True)

    # localizacion
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    region = Column(String, nullable=True)
    address = Column(String, nullable=True) 
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Variables
    working_status = Column(Boolean, nullable=True)
    visits_per_week = Column(Integer, default=1)
    visit_duration_seconds = Column(Integer, default=1800) 
    priority = Column(Integer, default=1)
    last_visited_at = Column(DateTime, nullable=True)

    visits = relationship("DailyVisit", back_populates="point_of_stop")

class DailyVisit (Base):
    __tablename__ = "daily_visits"

    id = Column(Integer, primary_key=True, index=True)
    visit_date = Column(Date, nullable=False, index=True)
    visit_order = Column(Integer, nullable=True)

    duration_from_previous_seconds = Column(Integer, nullable=True)
    estimated_arrival_time = Column(String, nullable=True)
    estimated_departure_time = Column(String, nullable=True)

    status = Column(Enum(VisitStatus), default=VisitStatus.PENDING)
    user_id = Column(Integer, ForeignKey("users.id"))
    point_of_stop_id = Column(Integer, ForeignKey("point_of_stops.id"))

    user = relationship("User", back_populates="visits")
    point_of_stop = relationship("PointOfStop", back_populates="visits")

    optimization_run_id = Column(Integer, ForeignKey("optimization_runs.id"), nullable=True)
    optimization_run = relationship("OptimizationRun", back_populates="daily_visits")

class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    optimization_run_id = Column(Integer, ForeignKey("optimization_runs.id"), nullable=True)
    optimization_run = relationship("OptimizationRun", back_populates="weekly_plans")

    user = relationship("User", back_populates="weekly_plans")
    total_pos_assigned = Column(Integer, default=0)

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

    weekly_plans = relationship("WeeklyPlan", back_populates="optimization_run")
    daily_visits = relationship("DailyVisit", back_populates="optimization_run")

    total_pdvs_assigned = Column(Integer, default=0)
    total_pdvs_unassigned = Column(Integer, default=0)

    total_visits_missed = Column(Integer, default=0)



class UserDistanceCache(Base):
    __tablename__ = "distance_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    origin_id = Column(Integer, ForeignKey ("users.id"))
    dest_id = Column(Integer, ForeignKey ("point_of_stops.id"))

    distance_meters = Column(Integer)
    duration_seconds = Column(Integer)
    cached_at = Column(DateTime(timezone=True), server_default=func.now())

class POSDistanceCache(Base):
    __tablename__ = "pos_distance_cache"
    
    id = Column(Integer, primary_key=True, index=True)

    origin_pos_id = Column(Integer, ForeignKey("point_of_stops.id"), index=True)

    dest_pos_id = Column(Integer, ForeignKey("point_of_stops.id"), index=True)

    distance_meters = Column(Integer)
    duration_seconds = Column(Integer)
    cached_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('origin_pos_id', 'dest_pos_id', name='_origin_dest_uc'),
    )