import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    first_name = Column(String, default="")
    last_name = Column(String, default="")
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(Integer, default=0)  # 0: user, 1: admin
    status = Column(Integer, default=1)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    google_access_token = Column(String, nullable=True)
    google_refresh_token = Column(String, nullable=True)
