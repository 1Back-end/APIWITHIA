from dataclasses import dataclass
from sqlalchemy.sql import func
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy import event
from app.main.models.db.base_class import Base
from enum import Enum


class UserRole(str,Enum):
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

class UserStatus(str,Enum):
    ACTIVED = "ACTIVED"
    UNACTIVED = "UNACTIVED"
    DELETED = "DELETED"
    BLOCKED= "BLOCKED"


class User(Base):
    __tablename__ = "users"

    uuid = Column(String,primary_key=True,index=True)
    email = Column(String,unique=True,index=True,nullable=False)
    country_code: str = Column(String(5), nullable=False, default="", index=True)
    phone_number: str = Column(String(20), nullable=False, default="", index=True)
    full_phone_number: str = Column(String(25), nullable=False, default="", index=True)
    first_name = Column(String,nullable=False)
    last_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role=Column(String,nullable=False)
    otp: str = Column(String(5), nullable=True, default="")
    otp_expired_at: datetime = Column(DateTime, nullable=True, default=None)
    otp_password: str = Column(String(5), nullable=True, default="")
    otp_password_expired_at: datetime = Column(DateTime, nullable=True, default=None)
    status = Column(String,nullable=False,default=UserStatus.ACTIVED)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"User('{self.first_name} {self.last_name}', '{self.email}')"