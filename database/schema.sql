CREATE DATABASE university_timetable;

-- Schools table
CREATE TABLE schools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Departments table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL UNIQUE,
    school_id INTEGER REFERENCES schools(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rooms table
CREATE TABLE rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL,
    room_type VARCHAR(20) NOT NULL CHECK (room_type IN ('normal', 'lab')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lecturers table
CREATE TABLE lecturers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    employment_type VARCHAR(20) NOT NULL CHECK (employment_type IN ('full_time', 'part_time')),
    max_units INTEGER NOT NULL,
    phone VARCHAR(15),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Units table
CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    department_id INTEGER REFERENCES departments(id),
    year_level INTEGER NOT NULL CHECK (year_level BETWEEN 1 AND 4),
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 2),
    requires_lab BOOLEAN DEFAULT FALSE,
    lecturer_id INTEGER REFERENCES lecturers(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student groups table (for tracking year-department combinations)
CREATE TABLE student_groups (
    id SERIAL PRIMARY KEY,
    department_id INTEGER REFERENCES departments(id),
    year_level INTEGER NOT NULL CHECK (year_level BETWEEN 1 AND 4),
    group_size INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Time slots table
CREATE TABLE time_slots (
    id SERIAL PRIMARY KEY,
    day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 1 AND 5), -- Monday = 1, Friday = 5
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    session_type VARCHAR(20) NOT NULL CHECK (session_type IN ('spas_3h', 'shs_2h')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Timetable entries table
CREATE TABLE timetable_entries (
    id SERIAL PRIMARY KEY,
    unit_id INTEGER REFERENCES units(id),
    lecturer_id INTEGER REFERENCES lecturers(id),
    room_id INTEGER REFERENCES rooms(id),
    time_slot_id INTEGER REFERENCES time_slots(id),
    student_group_id INTEGER REFERENCES student_groups(id),
    week_type VARCHAR(20) DEFAULT 'all' CHECK (week_type IN ('all', 'odd', 'even')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(room_id, time_slot_id),
    UNIQUE(lecturer_id, time_slot_id),
    UNIQUE(student_group_id, time_slot_id)
);