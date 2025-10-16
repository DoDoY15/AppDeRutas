from sqlalchemy import Boolean, Column, Integer, String, Float, Date, Enum, ForeignKey
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
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    visits = relationship("DailyVisit", back_populates="user")

class PointOfStop(Base):
    
    # identificacao 

    __tablename__ = "point_of_stops"
    external_id = Column(String, unique=True, index=True, nullable=True)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    chain = Column(String, nullable=True)
    Segment = Column(String, nullable=True)
    channel = Column(String, nullable=True)
    
    # localizacao

    City = Column(String, nullable=True)
    Country = Column(String, nullable=True)
    Region = Column(String, nullable=True)
    Address = Column(String, nullable=True) 
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Variaveis

    WorkingStatus = Column(Boolean, nullable=True)
    visits_per_week = Column(Integer, default=1)
    visit_duration_hours = Column(Integer, default=1) 
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

class DistanceCache(Base):
    __tablename__ = "distance_cache"
    id = Column(Integer, primary_key=True, index=True)
    origin_lat = Column(Float, nullable=False)
    origin_lng = Column(Float, nullable=False)
    dest_lat = Column(Float, nullable=False)
    dest_lng = Column(Float, nullable=False)
    distance_meters = Column(Integer)
    duration_seconds = Column(Integer)