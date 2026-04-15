import datetime
from enum import IntEnum
from sqlalchemy import Column, DateTime, Integer, String
from app.models.base import Base


class RoomStatus(IntEnum):
    UNAVAILABLE = 0
    AVAILABLE = 1


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    number_room = Column(String)
    address = Column(String)
    capacity = Column(Integer)
    status = Column(Integer, default=RoomStatus.AVAILABLE.value)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)