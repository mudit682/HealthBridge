# models.py
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
import enum

class UserType(str, enum.Enum):
    HOSPITAL = "hospital"
    GOVERNMENT = "government"
    CITIZEN = "citizen"

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    hospital_type = Column(String)
    admin_name = Column(String)
    position = Column(String)
    email = Column(String, unique=True, index=True)
    contact_number = Column(String)
    password_hash = Column(String)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # Add this line

    # Relationships
    resources = relationship("HospitalResource", back_populates="hospital")
    inventory = relationship("Inventory", back_populates="hospital")



class HospitalResource(Base):
    __tablename__ = "hospital_resources"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    general_beds_total = Column(Integer, default=0)
    general_beds_available = Column(Integer, default=0)
    icu_beds_total = Column(Integer, default=0)
    icu_beds_available = Column(Integer, default=0)
    emergency_beds_total = Column(Integer, default=0)
    emergency_beds_available = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    hospital = relationship("Hospital", back_populates="resources")

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"))
    item_name = Column(String)  # e.g., "Surgical Masks", "Oxygen Cylinders"
    quantity = Column(Integer)
    status = Column(String)  # "Adequate", "Low", etc
    last_updated = Column(DateTime, default=datetime.utcnow)

    hospital = relationship("Hospital", back_populates="inventory")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    user_type = Column(Enum(UserType))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)