import datetime
from enum import IntEnum
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from app.models.base import Base


class MeetingStatus(IntEnum):
    CANCELED = 0
    SCHEDULED = 1
    COMPLETED = 2


class MeetingType(IntEnum):
    IN_PERSON = 0
    ONLINE = 1
    HYBRID = 2


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    title = Column(Text)
    description = Column(Text)
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    organizer_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Integer, default=MeetingStatus.SCHEDULED.value)  # 0: canceled, 1: scheduled, 2: completed
    type = Column(Integer, default=MeetingType.IN_PERSON.value)  # 0: in-person, 1: online, 2: hybrid
    link = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)