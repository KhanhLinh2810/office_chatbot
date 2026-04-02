import datetime
from sqlalchemy import Column, DateTime, Integer, String
from app.models.base import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True)
    number_room = Column(String)
    address = Column(String)
    capacity = Column(Integer)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)