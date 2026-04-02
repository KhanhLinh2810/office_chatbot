import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.models.base import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    title = Column(Text)
    description = Column(Text)
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    organizer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Integer, default=1)
    type = Column(Integer, default=0)
    link = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)