# /main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from models.database_models import SessionLocal, engine, Base
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
from models.pydantic_models import (
    TimetableResponse, 
    ValidationResult,
    School as PydanticSchool,
    Department as PydanticDepartment,
    Lecturer as PydanticLecturer,
    Unit as PydanticUnit,
    Room as PydanticRoom,
    StudentGroup as PydanticStudentGroup
)
from services.scheduler import TimetableScheduler
from services.data_generator import DataGenerator

app = FastAPI(title="University Timetable System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add startup event handler
@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    try:
        print("🚀 Starting University Timetable System...")
        print("📊 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        print("🌐 API is ready to use!")
    except Exception as e:
        print(f"❌ Error during startup: {e}")

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check endpoint (move this to the top for easier testing)
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "University Timetable System"}

# Initialize data endpoints
@app.post("/api/initialize/sample-data")
async def initialize_sample_data(db: Session = Depends(get_db)):
    """Initialize the database with sample data"""
    try:
        generator = DataGenerator(db)
        generator.generate_sample_data()
        
        # Generate time slots
        scheduler = TimetableScheduler(db)
        scheduler.generate_time_slots()
        
        return {"message": "Sample data initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/timetable/generate")
async def generate_timetable(db: Session = Depends(get_db)):
    """Generate optimized timetable"""
    try:
        # Clear existing timetable entries - use the database model
        db.query(DBTimetableEntry).delete()
        db.commit()
        
        scheduler = TimetableScheduler(db)
        entries = scheduler.generate_schedule()
        
        return {
            "message": f"Timetable generated successfully with {len(entries)} entries",
            "entries_count": len(entries)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/timetable/validate")
async def validate_timetable(db: Session = Depends(get_db)):
    """Validate current timetable for conflicts"""
    try:
        entries = db.query(DBTimetableEntry).all()
        scheduler = TimetableScheduler(db)
        validation_result = scheduler.validate_constraints(entries)
        
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/timetable/view", response_model=List[TimetableResponse])
async def get_timetable(db: Session = Depends(get_db)):
    """Get formatted timetable for frontend consumption"""
    try:
        entries = db.query(DBTimetableEntry).all()
        formatted_entries = []
        
        for entry in entries:
            # Get related data using database models
            unit = db.query(DBUnit).filter(DBUnit.id == entry.unit_id).first()
            lecturer = db.query(DBLecturer).filter(DBLecturer.id == entry.lecturer_id).first()
            room = db.query(DBRoom).filter(DBRoom.id == entry.room_id).first()
            time_slot = db.query(DBTimeSlot).filter(DBTimeSlot.id == entry.time_slot_id).first()
            department = db.query(DBDepartment).filter(DBDepartment.id == unit.department_id).first()
            
            day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
            
            formatted_entry = TimetableResponse(
                course=unit.name,
                lecturer=lecturer.name,
                department=department.name,
                day=day_names[time_slot.day_of_week],
                start_time=time_slot.start_time.strftime("%H:%M"),
                end_time=time_slot.end_time.strftime("%H:%M"),
                room=room.name,
                year_level=unit.year_level,
                requires_lab=unit.requires_lab
            )
            
            formatted_entries.append(formatted_entry)
        
        return formatted_entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update all other endpoints to use the DB prefixed models
@app.get("/api/timetable/by-department/{department_code}")
async def get_timetable_by_department(
    department_code: str, 
    db: Session = Depends(get_db)
):
    """Get timetable filtered by department"""
    try:
        department = db.query(DBDepartment).filter(DBDepartment.code == department_code).first()
        if not department:
            raise HTTPException(status_code=404, detail="Department not found")
        
        # Get units for this department
        units = db.query(DBUnit).filter(DBUnit.department_id == department.id).all()
        unit_ids = [u.id for u in units]
        
        # Get timetable entries for these units
        entries = db.query(DBTimetableEntry).filter(DBTimetableEntry.unit_id.in_(unit_ids)).all()
        
        formatted_entries = []
        for entry in entries:
            unit = db.query(DBUnit).filter(DBUnit.id == entry.unit_id).first()
            lecturer = db.query(DBLecturer).filter(DBLecturer.id == entry.lecturer_id).first()
            room = db.query(DBRoom).filter(DBRoom.id == entry.room_id).first()
            time_slot = db.query(DBTimeSlot).filter(DBTimeSlot.id == entry.time_slot_id).first()
            
            day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
            
            formatted_entry = TimetableResponse(
                course=unit.name,
                lecturer=lecturer.name,
                department=department.name,
                day=day_names[time_slot.day_of_week],
                start_time=time_slot.start_time.strftime("%H:%M"),
                end_time=time_slot.end_time.strftime("%H:%M"),
                room=room.name,
                year_level=unit.year_level,
                requires_lab=unit.requires_lab
            )
            
            formatted_entries.append(formatted_entry)
        
        return formatted_entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/timetable/by-lecturer/{lecturer_id}")
async def get_timetable_by_lecturer(
    lecturer_id: int, 
    db: Session = Depends(get_db)
):
    """Get timetable filtered by lecturer"""
    try:
        lecturer = db.query(DBLecturer).filter(DBLecturer.id == lecturer_id).first()
        if not lecturer:
            raise HTTPException(status_code=404, detail="Lecturer not found")
        
        entries = db.query(DBTimetableEntry).filter(DBTimetableEntry.lecturer_id == lecturer_id).all()
        
        formatted_entries = []
        for entry in entries:
            unit = db.query(DBUnit).filter(DBUnit.id == entry.unit_id).first()
            room = db.query(DBRoom).filter(DBRoom.id == entry.room_id).first()
            time_slot = db.query(DBTimeSlot).filter(DBTimeSlot.id == entry.time_slot_id).first()
            department = db.query(DBDepartment).filter(DBDepartment.id == unit.department_id).first()
            
            day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
            
            formatted_entry = TimetableResponse(
                course=unit.name,
                lecturer=lecturer.name,
                department=department.name,
                day=day_names[time_slot.day_of_week],
                start_time=time_slot.start_time.strftime("%H:%M"),
                end_time=time_slot.end_time.strftime("%H:%M"),
                room=room.name,
                year_level=unit.year_level,
                requires_lab=unit.requires_lab
            )
            
            formatted_entries.append(formatted_entry)
        
        return formatted_entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# CRUD endpoints for entities
@app.get("/api/schools", response_model=List[PydanticSchool])
async def get_schools(db: Session = Depends(get_db)):
    """Get all schools"""
    return db.query(DBSchool).all()

@app.get("/api/departments", response_model=List[PydanticDepartment])
async def get_departments(db: Session = Depends(get_db)):
    """Get all departments"""
    return db.query(DBDepartment).all()

@app.get("/api/lecturers", response_model=List[PydanticLecturer])
async def get_lecturers(db: Session = Depends(get_db)):
    """Get all lecturers"""
    return db.query(DBLecturer).all()

@app.get("/api/units", response_model=List[PydanticUnit])
async def get_units(db: Session = Depends(get_db)):
    """Get all units"""
    return db.query(DBUnit).all()

@app.get("/api/rooms", response_model=List[PydanticRoom])
async def get_rooms(db: Session = Depends(get_db)):
    """Get all rooms"""
    return db.query(DBRoom).all()

@app.get("/api/student-groups", response_model=List[PydanticStudentGroup])
async def get_student_groups(db: Session = Depends(get_db)):
    """Get all student groups"""
    return db.query(DBStudentGroup).all()

@app.get("/api/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Get system statistics"""
    try:
        stats = {
            "total_schools": db.query(DBSchool).count(),
            "total_departments": db.query(DBDepartment).count(),
            "total_lecturers": db.query(DBLecturer).count(),
            "total_units": db.query(DBUnit).count(),
            "total_rooms": db.query(DBRoom).count(),
            "total_student_groups": db.query(DBStudentGroup).count(),
            "total_timetable_entries": db.query(DBTimetableEntry).count(),
            "lab_rooms": db.query(DBRoom).filter(DBRoom.room_type == "lab").count(),
            "normal_rooms": db.query(DBRoom).filter(DBRoom.room_type == "normal").count(),
            "full_time_lecturers": db.query(DBLecturer).filter(DBLecturer.employment_type == "full_time").count(),
            "part_time_lecturers": db.query(DBLecturer).filter(DBLecturer.employment_type == "part_time").count(),
            "units_requiring_lab": db.query(DBUnit).filter(DBUnit.requires_lab == True).count(),
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/timetable/conflicts")
async def get_conflicts(db: Session = Depends(get_db)):
    """Get detailed conflict analysis"""
    try:
        entries = db.query(DBTimetableEntry).all()
        conflicts = []
        
        # Group by time slot
        from collections import defaultdict
        slot_groups = defaultdict(list)
        
        for entry in entries:
            slot_groups[entry.time_slot_id].append(entry)
        
        for slot_id, slot_entries in slot_groups.items():
            if len(slot_entries) > 1:
                time_slot = db.query(DBTimeSlot).filter(DBTimeSlot.id == slot_id).first()
                day_names = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday"}
                
                # Check for lecturer conflicts
                lecturers = [e.lecturer_id for e in slot_entries]
                if len(set(lecturers)) != len(lecturers):
                    lecturer_conflicts = defaultdict(list)
                    for entry in slot_entries:
                        lecturer_conflicts[entry.lecturer_id].append(entry)
                    
                    for lecturer_id, conflicting_entries in lecturer_conflicts.items():
                        if len(conflicting_entries) > 1:
                            lecturer = db.query(DBLecturer).filter(DBLecturer.id == lecturer_id).first()
                            conflicts.append({
                                "type": "lecturer_conflict",
                                "day": day_names[time_slot.day_of_week],
                                "time": f"{time_slot.start_time} - {time_slot.end_time}",
                                "lecturer": lecturer.name,
                                "conflicting_units": [
                                    db.query(DBUnit).filter(DBUnit.id == e.unit_id).first().name 
                                    for e in conflicting_entries
                                ]
                            })
        
        return {"conflicts": conflicts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add a debug endpoint to check what data exists
@app.get("/api/debug/data-check")
async def debug_data_check(db: Session = Depends(get_db)):
    """Debug endpoint to check what data exists"""
    try:
        schools_count = db.query(DBSchool).count()
        departments_count = db.query(DBDepartment).count()
        units_count = db.query(DBUnit).count()
        lecturers_count = db.query(DBLecturer).count()
        rooms_count = db.query(DBRoom).count()
        time_slots_count = db.query(DBTimeSlot).count()
        student_groups_count = db.query(DBStudentGroup).count()
        
        # Get sample data
        sample_units = db.query(DBUnit).limit(5).all()
        sample_time_slots = db.query(DBTimeSlot).limit(5).all()
        sample_rooms = db.query(DBRoom).all()
        
        return {
            "counts": {
                "schools": schools_count,
                "departments": departments_count,
                "units": units_count,
                "lecturers": lecturers_count,
                "rooms": rooms_count,
                "time_slots": time_slots_count,
                "student_groups": student_groups_count
            },
            "sample_units": [
                {
                    "id": u.id,
                    "name": u.name,
                    "requires_lab": u.requires_lab,
                    "department_id": u.department_id,
                    "year_level": u.year_level
                } for u in sample_units
            ],
            "sample_time_slots": [
                {
                    "id": ts.id,
                    "day": ts.day_of_week,
                    "start_time": str(ts.start_time),
                    "session_type": ts.session_type
                } for ts in sample_time_slots
            ],
            "rooms": [
                {
                    "id": r.id,
                    "name": r.name,
                    "room_type": r.room_type
                } for r in sample_rooms
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/debug/regenerate-time-slots")
async def regenerate_time_slots(db: Session = Depends(get_db)):
    """Debug endpoint to regenerate time slots"""
    try:
        # Clear existing time slots
        db.query(DBTimeSlot).delete()
        db.commit()
        
        # Generate new time slots
        scheduler = TimetableScheduler(db)
        time_slots = scheduler.generate_time_slots()
        
        return {
            "message": f"Generated {len(time_slots)} time slots",
            "time_slots_count": len(time_slots)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)