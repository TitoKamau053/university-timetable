import random
from sqlalchemy.orm import Session
from models.database_models import (
    School as DBSchool,
    Department as DBDepartment,
    Room as DBRoom,
    Lecturer as DBLecturer,
    Unit as DBUnit,
    StudentGroup as DBStudentGroup
)
from collections import defaultdict

class DataGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.kenyan_names = [
            "Wanjiku Kamau", "Otieno Ochieng", "Njoroge Mwangi", "Akinyi Adhiambo", 
            "Kipchoge Rotich", "Nyambura Kariuki", "Omondi Owino", "Wanjiru Ndungu",
            "Kiprotich Chelimo", "Wairimu Githinji", "Ombima Nyong'o", "Nduta Waweru",
            "Kimani Macharia", "Auma Ogola", "Karanja Njeri", "Chebet Korir",
            "Mwenda Mutua", "Awuor Oduya", "Gathoni Mbugua", "Kiplagat Suter",
            "Mukami Githuka", "Odongo Obong'o", "Wangari Maathai", "Talam Chepkwony",
            "Njeri Wanjiku", "Odhiambo Otieno", "Githui Kamunde", "Moraa Gesare",
            "Kibet Lagat", "Wambui Karanja", "Okello Otieno", "Njambi Koigi",
            "Rutto Kiplangat", "Wangui Ndung'u", "Oyugi Awuondo", "Muthoni Kimemia",
            "Chepkurui Rotich", "Waiguru Kamotho", "Ochieng Oduor", "Njoki Wanjiru",
            "Kiprono Cheruiyot", "Wambugu Kamau", "Anyango Onyango", "Gitonga Mwangi",
            "Jeptoo Kibet", "Muhoro Ndegwa", "Akoth Omondi", "Njuguna Kariuki",
            "Chelimo Kipchoge", "Wangechi Mburu"
        ]
    
    def generate_sample_data(self):
        """Generate all sample data for the university"""
        self.create_schools_and_departments()
        self.create_rooms()
        self.create_lecturers()
        self.create_units()
        self.create_student_groups()
    
    def create_schools_and_departments(self):
        """Create schools and departments"""
        # Check if schools already exist
        existing_spas = self.db.query(DBSchool).filter(DBSchool.code == "SPAS").first()
        existing_shs = self.db.query(DBSchool).filter(DBSchool.code == "SHS").first()
        
        if existing_spas and existing_shs:
            print("Schools already exist, skipping school creation")
            return
        
        # Create SPAS if it doesn't exist
        if not existing_spas:
            spas = DBSchool(name="School of Pure and Applied Sciences", code="SPAS")
            self.db.add(spas)
            self.db.flush()
            
            itcs_dept = DBDepartment(name="Information Technology and Computer Science", code="ITCS", school_id=spas.id)
            mac_dept = DBDepartment(name="Mathematics and Computing", code="MAC", school_id=spas.id)
            self.db.add_all([itcs_dept, mac_dept])
        
        # Create SHS if it doesn't exist
        if not existing_shs:
            shs = DBSchool(name="School of Health Sciences", code="SHS")
            self.db.add(shs)
            self.db.flush()
            
            nursing_dept = DBDepartment(name="Nursing", code="NURS", school_id=shs.id)
            psych_dept = DBDepartment(name="Psychology", code="PSYC", school_id=shs.id)
            self.db.add_all([nursing_dept, psych_dept])
        
        self.db.commit()

    def create_rooms(self):
        """Create 20 rooms (18 normal, 2 lab)"""
        # Check if rooms already exist
        existing_rooms = self.db.query(DBRoom).count()
        if existing_rooms > 0:
            print(f"Rooms already exist ({existing_rooms} found), skipping room creation")
            return
        
        rooms = []
        
        # Normal rooms
        for i in range(1, 19):
            rooms.append(DBRoom(
                name=f"Room {i:02d}",
                capacity=random.randint(30, 80),
                room_type="normal"
            ))
        
        # Lab rooms
        rooms.append(DBRoom(name="Computer Lab A", capacity=40, room_type="lab"))
        rooms.append(DBRoom(name="Computer Lab B", capacity=35, room_type="lab"))
        
        self.db.add_all(rooms)
        self.db.commit()
    
    def create_lecturers(self):
        """Create 50 lecturers (30 full-time, 20 part-time)"""
        # Check if lecturers already exist
        existing_lecturers = self.db.query(DBLecturer).count()
        if existing_lecturers > 0:
            print(f"Lecturers already exist ({existing_lecturers} found), skipping lecturer creation")
            return
        
        lecturers = []
        names_copy = self.kenyan_names.copy()
        random.shuffle(names_copy)
        
        # Full-time lecturers (4 units each)
        for i in range(30):
            lecturers.append(DBLecturer(
                name=names_copy[i],
                employee_id=f"FT{i+1:03d}",
                employment_type="full_time",
                max_units=4,
                phone=f"254{random.randint(700000000, 799999999)}",
                email=f"{names_copy[i].lower().replace(' ', '.')}@university.ac.ke"
            ))
        
        # Part-time lecturers (2 units each)
        for i in range(20):
            lecturers.append(DBLecturer(
                name=names_copy[30 + i],
                employee_id=f"PT{i+1:03d}",
                employment_type="part_time",
                max_units=2,
                phone=f"254{random.randint(700000000, 799999999)}",
                email=f"{names_copy[30 + i].lower().replace(' ', '.')}@university.ac.ke"
            ))
        
        self.db.add_all(lecturers)
        self.db.commit()
    
    def create_units(self):
        """Create 100 units distributed across departments"""
        # Check if units already exist
        existing_units = self.db.query(DBUnit).count()
        if existing_units > 0:
            print(f"Units already exist ({existing_units} found), skipping unit creation")
            return
        
        departments = self.db.query(DBDepartment).all()
        lecturers = self.db.query(DBLecturer).all()
        
        # Track lecturer unit counts
        lecturer_units = defaultdict(int)
        
        units = []
        unit_counter = 1
        
        # Subject areas for each department
        subjects = {
            "ITCS": ["Programming", "Database Systems", "Network Security", "Web Development", 
                    "Data Structures", "Software Engineering", "Mobile Computing", "AI", 
                    "Computer Graphics", "System Administration"],
            "MAC": ["Calculus", "Linear Algebra", "Statistics", "Discrete Mathematics",
                   "Numerical Analysis", "Operations Research", "Probability Theory",
                   "Mathematical Modeling", "Abstract Algebra", "Real Analysis"],
            "NURS": ["Anatomy", "Physiology", "Pharmacology", "Medical Nursing",
                    "Surgical Nursing", "Community Health", "Mental Health", "Pediatric Nursing",
                    "Obstetrics", "Ethics in Nursing"],
            "PSYC": ["General Psychology", "Developmental Psychology", "Abnormal Psychology",
                    "Social Psychology", "Cognitive Psychology", "Research Methods",
                    "Counseling Psychology", "Educational Psychology", "Clinical Psychology",
                    "Personality Theory"]
        }
        
        for dept in departments:
            dept_subjects = subjects[dept.code]
            units_per_dept = 25  # 100 units / 4 departments
            
            for i in range(units_per_dept):
                # Find lecturer with available capacity
                available_lecturers = [l for l in lecturers if lecturer_units[l.id] < l.max_units]
                if not available_lecturers:
                    break
                
                lecturer = random.choice(available_lecturers)
                
                subject = random.choice(dept_subjects)
                year_level = random.randint(1, 4)
                semester = random.randint(1, 2)
                
                # Determine if unit requires lab (higher probability for ITCS)
                requires_lab = False
                if dept.code == "ITCS":
                    requires_lab = random.random() < 0.4  # 40% chance for ITCS
                elif dept.code == "MAC":
                    requires_lab = random.random() < 0.2  # 20% chance for MAC
                
                unit = DBUnit(
                    name=f"{subject} {year_level}",
                    code=f"{dept.code}{unit_counter:03d}",
                    department_id=dept.id,
                    year_level=year_level,
                    semester=semester,
                    requires_lab=requires_lab,
                    lecturer_id=lecturer.id
                )
                
                units.append(unit)
                lecturer_units[lecturer.id] += 1
                unit_counter += 1
        
        self.db.add_all(units)
        self.db.commit()
    
    def create_student_groups(self):
        """Create student groups for each department and year level"""
        # Check if student groups already exist
        existing_groups = self.db.query(DBStudentGroup).count()
        if existing_groups > 0:
            print(f"Student groups already exist ({existing_groups} found), skipping student group creation")
            return
        
        departments = self.db.query(DBDepartment).all()
        student_groups = []
        
        for dept in departments:
            for year in range(1, 5):  # Years 1-4
                group_size = random.randint(25, 60)
                student_group = DBStudentGroup(
                    department_id=dept.id,
                    year_level=year,
                    group_size=group_size
                )
                student_groups.append(student_group)
        
        self.db.add_all(student_groups)
        self.db.commit()