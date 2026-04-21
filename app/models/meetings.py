import datetime
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from app.models.base import Base
from app.models.enums import MeetingStatus, MeetingType


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    title = Column(Text)
    description = Column(Text)
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    organizer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(MeetingStatus), default=MeetingStatus.SCHEDULED)  # 0: canceled, 1: scheduled, 2: completed
    type = Column(Enum(MeetingType), default=MeetingType.IN_PERSON)  # 0: in-person, 1: online, 2: hybrid
    link = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)