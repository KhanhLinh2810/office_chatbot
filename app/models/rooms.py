import datetime
from enum import Enum
from sqlalchemy import Column, DateTime, Integer, String, Enum as SAEnum
from app.models.base import Base


class RoomStatus(Enum):
    UNAVAILABLE = 0
    AVAILABLE = 1


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    number_room = Column(String)
    address = Column(String)
    capacity = Column(Integer)
    status = Column(SAEnum(RoomStatus), default=RoomStatus.AVAILABLE)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)