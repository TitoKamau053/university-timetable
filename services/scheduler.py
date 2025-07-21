from typing import List, Dict, Tuple, Set
from sqlalchemy.orm import Session
# Import database models with DB prefix to avoid conflicts
from models.database_models import (
    TimetableEntry as DBTimetableEntry,
    Unit as DBUnit,
    Lecturer as DBLecturer,
    Room as DBRoom,
    TimeSlot as DBTimeSlot,
    Department as DBDepartment,
    School as DBSchool,
    StudentGroup as DBStudentGroup
)
from models.pydantic_models import ValidationResult
from datetime import time, timedelta
import random
from collections import defaultdict

class TimetableScheduler:
    def __init__(self, db: Session):
        self.db = db
        self.day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
        
    def generate_time_slots(self):
        """Generate time slots based on school requirements"""
        time_slots = []
        
        # SPAS time slots (3-hour sessions)
        spas_sessions = [
            (time(7, 0), time(10, 0)),   # 7:00 AM - 10:00 AM
            (time(10, 30), time(13, 30)), # 10:30 AM - 1:30 PM (after tea break)
            (time(14, 0), time(17, 0)),   # 2:00 PM - 5:00 PM (after lunch break)
            (time(16, 0), time(19, 0)),   # 4:00 PM - 7:00 PM
        ]
        
        # SHS time slots (2-hour sessions)
        shs_sessions = [
            (time(7, 0), time(9, 0)),     # 7:00 AM - 9:00 AM
            (time(9, 0), time(11, 0)),    # 9:00 AM - 11:00 AM
            (time(11, 0), time(13, 0)),   # 11:00 AM - 1:00 PM
            (time(14, 0), time(16, 0)),   # 2:00 PM - 4:00 PM
            (time(16, 0), time(18, 0)),   # 4:00 PM - 6:00 PM
            (time(17, 0), time(19, 0)),   # 5:00 PM - 7:00 PM
        ]
        
        for day in range(1, 6):  # Monday to Friday
            # Add SPAS sessions
            for start, end in spas_sessions:
                time_slots.append(DBTimeSlot(
                    day_of_week=day,
                    start_time=start,
                    end_time=end,
                    session_type="spas_3h"
                ))
            
            # Add SHS sessions
            for start, end in shs_sessions:
                time_slots.append(DBTimeSlot(
                    day_of_week=day,
                    start_time=start,
                    end_time=end,
                    session_type="shs_2h"
                ))
        
        # Save to database
        self.db.add_all(time_slots)
        self.db.commit()
        return time_slots
    
    def validate_constraints(self, timetable_entries: List[DBTimetableEntry]) -> ValidationResult:
        """Validate timetable constraints"""
        conflicts = []
        warnings = []
        
        # Group entries by time slot
        slot_bookings = defaultdict(list)
        lecturer_bookings = defaultdict(list)
        student_bookings = defaultdict(list)
        room_bookings = defaultdict(list)
        
        for entry in timetable_entries:
            slot_id = entry.time_slot_id
            slot_bookings[slot_id].append(entry)
            lecturer_bookings[entry.lecturer_id].append(entry)
            student_bookings[entry.student_group_id].append(entry)
            room_bookings[entry.room_id].append(entry)
        
        # Check for double bookings
        for slot_id, entries in slot_bookings.items():
            lecturers = [e.lecturer_id for e in entries]
            rooms = [e.room_id for e in entries]
            students = [e.student_group_id for e in entries]
            
            if len(set(lecturers)) != len(lecturers):
                conflicts.append(f"Lecturer double-booked in time slot {slot_id}")
            
            if len(set(rooms)) != len(rooms):
                conflicts.append(f"Room double-booked in time slot {slot_id}")
            
            if len(set(students)) != len(students):
                conflicts.append(f"Student group double-booked in time slot {slot_id}")
        
        # Check lab requirements
        for entry in timetable_entries:
            unit = self.db.query(DBUnit).filter(DBUnit.id == entry.unit_id).first()
            room = self.db.query(DBRoom).filter(DBRoom.id == entry.room_id).first()
            
            if unit and room:
                if unit.requires_lab and room.room_type != "lab":
                    conflicts.append(f"Lab unit {unit.code} assigned to non-lab room {room.name}")
        
        return ValidationResult(
            is_valid=len(conflicts) == 0,
            conflicts=conflicts,
            warnings=warnings
        )
    
    def generate_schedule(self) -> List[DBTimetableEntry]:
        """Generate optimized timetable using constraint programming approach"""
        
        # Get all entities using database models
        units = self.db.query(DBUnit).all()
        lecturers = self.db.query(DBLecturer).all()
        rooms = self.db.query(DBRoom).all()
        time_slots = self.db.query(DBTimeSlot).all()
        student_groups = self.db.query(DBStudentGroup).all()
        
        print(f"🔍 Debug: Found {len(units)} units, {len(time_slots)} time slots, {len(rooms)} rooms")
        
        if not units:
            print("❌ No units found!")
            return []
        
        if not time_slots:
            print("❌ No time slots found!")
            return []
        
        if not rooms:
            print("❌ No rooms found!")
            return []
        
        # Create mappings
        lecturer_units = defaultdict(list)
        for unit in units:
            lecturer_units[unit.lecturer_id].append(unit)
        
        # Initialize tracking structures
        lecturer_schedule = defaultdict(set)
        room_schedule = defaultdict(set)
        student_schedule = defaultdict(set)
        
        timetable_entries = []
        
        # Sort units by priority (lab units first, then by year level)
        sorted_units = sorted(units, key=lambda u: (not u.requires_lab, u.year_level))
        
        print(f"🔄 Processing {len(sorted_units)} units...")
        
        for i, unit in enumerate(sorted_units):
            print(f"📚 Processing unit {i+1}/{len(sorted_units)}: {unit.name} (Lab: {unit.requires_lab})")
            
            # Find student group for this unit
            student_group = self.db.query(DBStudentGroup).filter(
                DBStudentGroup.department_id == unit.department_id,
                DBStudentGroup.year_level == unit.year_level
            ).first()
            
            if not student_group:
                print(f"⚠️  No student group found for unit {unit.name}")
                continue
            
            # Determine session type based on department's school
            dept = self.db.query(DBDepartment).filter(DBDepartment.id == unit.department_id).first()
            school = self.db.query(DBSchool).filter(DBSchool.id == dept.school_id).first()
            
            session_type = "spas_3h" if school.code == "SPAS" else "shs_2h"
            print(f"📋 Unit belongs to {school.code}, using {session_type} sessions")
            
            # Find suitable rooms
            if unit.requires_lab:
                suitable_rooms = [r for r in rooms if r.room_type == "lab"]
            else:
                suitable_rooms = [r for r in rooms if r.room_type == "normal"]
            
            print(f"🏢 Found {len(suitable_rooms)} suitable rooms")
            
            if not suitable_rooms:
                print(f"❌ No suitable rooms for unit {unit.name} (lab required: {unit.requires_lab})")
                continue
            
            # Find available time slots
            available_slots = [ts for ts in time_slots if ts.session_type == session_type]
            print(f"⏰ Found {len(available_slots)} available time slots for {session_type}")
            
            if not available_slots:
                print(f"❌ No time slots available for session type {session_type}")
                continue
            
            scheduled = False
            attempts = 0
            max_attempts = min(100, len(available_slots) * len(suitable_rooms))  # Limit attempts
            
            while not scheduled and attempts < max_attempts:
                # Randomly select slot and room to distribute load
                slot = random.choice(available_slots)
                room = random.choice(suitable_rooms)
                
                # Check conflicts
                slot_key = (slot.day_of_week, slot.start_time)
                
                lecturer_conflict = slot_key in lecturer_schedule[unit.lecturer_id]
                room_conflict = slot_key in room_schedule[room.id]
                student_conflict = slot_key in student_schedule[student_group.id]
                
                if not (lecturer_conflict or room_conflict or student_conflict):
                    # Schedule the unit
                    entry = DBTimetableEntry(
                        unit_id=unit.id,
                        lecturer_id=unit.lecturer_id,
                        room_id=room.id,
                        time_slot_id=slot.id,
                        student_group_id=student_group.id
                    )
                    
                    timetable_entries.append(entry)
                    
                    # Update tracking
                    lecturer_schedule[unit.lecturer_id].add(slot_key)
                    room_schedule[room.id].add(slot_key)
                    student_schedule[student_group.id].add(slot_key)
                    
                    scheduled = True
                    print(f"✅ Scheduled {unit.name} on {self.day_names[slot.day_of_week]} {slot.start_time}-{slot.end_time} in {room.name}")
                else:
                    conflicts = []
                    if lecturer_conflict:
                        conflicts.append("lecturer")
                    if room_conflict:
                        conflicts.append("room")
                    if student_conflict:
                        conflicts.append("student")
                    print(f"🔄 Attempt {attempts+1}: Conflicts - {', '.join(conflicts)}")
                
                attempts += 1
            
            if not scheduled:
                print(f"❌ Could not schedule unit {unit.code} after {attempts} attempts")
        
        print(f"💾 Saving {len(timetable_entries)} timetable entries to database...")
        
        # Save to database
        self.db.add_all(timetable_entries)
        self.db.commit()
        
        print(f"✅ Successfully created {len(timetable_entries)} timetable entries")
        return timetable_entries