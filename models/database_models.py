from sqlalchemy import create_engine, Column, Integer, String, Boolean, Time, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import time, datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Titus7833@gmail@localhost:5432/university_timetable")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class School(Base):
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    departments = relationship("Department", back_populates="school")

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    school_id = Column(Integer, ForeignKey("schools.id"))
    created_at = Column(DateTime, default=func.now())
    
    school = relationship("School", back_populates="departments")
    units = relationship("Unit", back_populates="department")
    student_groups = relationship("StudentGroup", back_populates="department")

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    room_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (CheckConstraint("room_type IN ('normal', 'lab')"),)
    
    timetable_entries = relationship("TimetableEntry", back_populates="room")

class Lecturer(Base):
    __tablename__ = "lecturers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    employee_id = Column(String(20), unique=True, nullable=False)
    employment_type = Column(String(20), nullable=False)
    max_units = Column(Integer, nullable=False)
    phone = Column(String(15))
    email = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (CheckConstraint("employment_type IN ('full_time', 'part_time')"),)
    
    units = relationship("Unit", back_populates="lecturer")
    timetable_entries = relationship("TimetableEntry", back_populates="lecturer")

class Unit(Base):
    __tablename__ = "units"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    year_level = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    requires_lab = Column(Boolean, default=False)
    lecturer_id = Column(Integer, ForeignKey("lecturers.id"))
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        CheckConstraint("year_level BETWEEN 1 AND 4"),
        CheckConstraint("semester BETWEEN 1 AND 2"),
    )
    
    department = relationship("Department", back_populates="units")
    lecturer = relationship("Lecturer", back_populates="units")
    timetable_entries = relationship("TimetableEntry", back_populates="unit")

class StudentGroup(Base):
    __tablename__ = "student_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    year_level = Column(Integer, nullable=False)
    group_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (CheckConstraint("year_level BETWEEN 1 AND 4"),)
    
    department = relationship("Department", back_populates="student_groups")
    timetable_entries = relationship("TimetableEntry", back_populates="student_group")

class TimeSlot(Base):
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Integer, nullable=False)  # 1=Monday, 5=Friday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    session_type = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 1 AND 5"),
        CheckConstraint("session_type IN ('spas_3h', 'shs_2h')"),
    )
    
    timetable_entries = relationship("TimetableEntry", back_populates="time_slot")

class TimetableEntry(Base):
    __tablename__ = "timetable_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"))
    lecturer_id = Column(Integer, ForeignKey("lecturers.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"))
    student_group_id = Column(Integer, ForeignKey("student_groups.id"))
    week_type = Column(String(20), default="all")
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (CheckConstraint("week_type IN ('all', 'odd', 'even')"),)
    
    unit = relationship("Unit", back_populates="timetable_entries")
    lecturer = relationship("Lecturer", back_populates="timetable_entries")
    room = relationship("Room", back_populates="timetable_entries")
    time_slot = relationship("TimeSlot", back_populates="timetable_entries")
    student_group = relationship("StudentGroup", back_populates="timetable_entries")