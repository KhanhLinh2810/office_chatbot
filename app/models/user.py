from sqlalchemy import Column, Integer, String
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    status = Column(Integer, default=1)
    google_access_token = Column(String, nullable=True)
    google_refresh_token = Column(String, nullable=True)
