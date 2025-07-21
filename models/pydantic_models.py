from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import time, datetime
from enum import Enum

class EmploymentType(str, Enum):
    full_time = "full_time"
    part_time = "part_time"

class RoomType(str, Enum):
    normal = "normal"
    lab = "lab"

class SessionType(str, Enum):
    spas_3h = "spas_3h"
    shs_2h = "shs_2h"

class WeekType(str, Enum):
    all = "all"
    odd = "odd"
    even = "even"

# Base schemas
class SchoolBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)

class SchoolCreate(SchoolBase):
    pass

class School(SchoolBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime

class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)
    school_id: int

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    school: School

class RoomBase(BaseModel):
    name: str = Field(..., max_length=50)
    capacity: int = Field(..., gt=0)
    room_type: RoomType

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime

class LecturerBase(BaseModel):
    name: str = Field(..., max_length=100)
    employee_id: str = Field(..., max_length=20)
    employment_type: EmploymentType
    max_units: int = Field(..., gt=0)
    phone: Optional[str] = Field(None, max_length=15)
    email: Optional[str] = Field(None, max_length=100)

class LecturerCreate(LecturerBase):
    pass

class Lecturer(LecturerBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime

class UnitBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)
    department_id: int
    year_level: int = Field(..., ge=1, le=4)
    semester: int = Field(..., ge=1, le=2)
    requires_lab: bool = False
    lecturer_id: int

class UnitCreate(UnitBase):
    pass

class Unit(UnitBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    department: Department
    lecturer: Lecturer

class StudentGroupBase(BaseModel):
    department_id: int
    year_level: int = Field(..., ge=1, le=4)
    group_size: int = Field(..., gt=0)

class StudentGroupCreate(StudentGroupBase):
    pass

class StudentGroup(StudentGroupBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    department: Department

class TimeSlotBase(BaseModel):
    day_of_week: int = Field(..., ge=1, le=5)
    start_time: time
    end_time: time
    session_type: SessionType

class TimeSlotCreate(TimeSlotBase):
    pass

class TimeSlot(TimeSlotBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime

class TimetableEntryBase(BaseModel):
    unit_id: int
    lecturer_id: int
    room_id: int
    time_slot_id: int
    student_group_id: int
    week_type: WeekType = WeekType.all

class TimetableEntryCreate(TimetableEntryBase):
    pass

class TimetableEntry(TimetableEntryBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    unit: Unit
    lecturer: Lecturer
    room: Room
    time_slot: TimeSlot
    student_group: StudentGroup

# Response schemas
class TimetableResponse(BaseModel):
    course: str
    lecturer: str
    department: str
    day: str
    start_time: str
    end_time: str
    room: str
    year_level: int
    requires_lab: bool

class ValidationResult(BaseModel):
    is_valid: bool
    conflicts: List[str]
    warnings: List[str]