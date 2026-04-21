import datetime
from sqlalchemy import Column, DateTime, Enum, Integer, String
from app.models.base import Base
from app.models.enums import RoomStatus


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    number_room = Column(String)
    address = Column(String)
    capacity = Column(Integer)
    status = Column(Enum(RoomStatus), default=RoomStatus.AVAILABLE)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)