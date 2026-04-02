import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from app.models.base import Base


class UserMeeting(Base):
    __tablename__ = "user_meetings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    role = Column(Integer, default=0)
    status = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)