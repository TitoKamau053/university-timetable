# /README.md
# University Timetable Management System

A comprehensive FastAPI-based system for managing university timetables with automated scheduling, conflict detection, and constraint optimization.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL database
- pip package manager

### Installation
1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file with database URL: `DATABASE_URL=postgresql://username:password@localhost:5432/university_timetable`
6. Run the application: `uvicorn main:app --reload`

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`

## 📋 API Endpoints Reference

### 🏥 Health Check
- **GET** `/health` - System health check
  ```json
  Response: {"status": "healthy", "service": "University Timetable System"}
  ```

### 🗄️ Data Initialization
- **POST** `/api/initialize/sample-data` - Initialize database with sample data
  ```json
  Response: {"message": "Sample data initialized successfully"}
  ```
- **POST** `/api/initialize/clear-all-data` - Clear all data from database
  ```json
  Response: {"message": "All data cleared successfully"}
  ```

### 📊 System Statistics
- **GET** `/api/statistics` - Get comprehensive system statistics
  ```json
  Response: {
    "total_schools": 2,
    "total_departments": 4,
    "total_lecturers": 50,
    "total_units": 100,
    "total_rooms": 20,
    "total_student_groups": 16,
    "total_timetable_entries": 85,
    "lab_rooms": 2,
    "normal_rooms": 18,
    "full_time_lecturers": 30,
    "part_time_lecturers": 20,
    "units_requiring_lab": 15
  }
  ```

### 🏫 Schools Management
- **GET** `/api/schools` - Get all schools
  ```json
  Response: [
    {
      "id": 1,
      "name": "School of Pure and Applied Sciences",
      "code": "SPAS",
      "created_at": "2025-07-20T10:30:00Z"
    },
    {
      "id": 2,
      "name": "School of Health Sciences", 
      "code": "SHS",
      "created_at": "2025-07-20T10:30:00Z"
    }
  ]
  ```

### 🏢 Departments Management
- **GET** `/api/departments` - Get all departments
  ```json
  Response: [
    {
      "id": 1,
      "name": "Information Technology and Computer Science",
      "code": "ITCS",
      "school_id": 1,
      "created_at": "2025-07-20T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Mathematics and Computing",
      "code": "MAC", 
      "school_id": 1,
      "created_at": "2025-07-20T10:30:00Z"
    }
  ]
  ```

### 👨‍🏫 Lecturers Management
- **GET** `/api/lecturers` - Get all lecturers
  ```json
  Response: [
    {
      "id": 1,
      "name": "Wanjiku Kamau",
      "employee_id": "FT001",
      "employment_type": "full_time",
      "max_units": 4,
      "phone": "254712345678",
      "email": "wanjiku.kamau@university.ac.ke",
      "created_at": "2025-07-20T10:30:00Z"
    }
  ]
  ```

### 📚 Units Management
- **GET** `/api/units` - Get all units/courses
  ```json
  Response: [
    {
      "id": 1,
      "name": "Programming 2",
      "code": "ITCS001",
      "department_id": 1,
      "year_level": 2,
      "semester": 1,
      "requires_lab": true,
      "lecturer_id": 1,
      "created_at": "2025-07-20T10:30:00Z"
    }
  ]
  ```

### 🏢 Rooms Management
- **GET** `/api/rooms` - Get all rooms
  ```json
  Response: [
    {
      "id": 1,
      "name": "Room 01",
      "capacity": 45,
      "room_type": "normal",
      "created_at": "2025-07-20T10:30:00Z"
    },
    {
      "id": 20,
      "name": "Computer Lab A",
      "capacity": 40,
      "room_type": "lab",
      "created_at": "2025-07-20T10:30:00Z"
    }
  ]
  ```

### 👥 Student Groups Management
- **GET** `/api/student-groups` - Get all student groups
  ```json
  Response: [
    {
      "id": 1,
      "department_id": 1,
      "year_level": 1,
      "group_size": 35,
      "created_at": "2025-07-20T10:30:00Z"
    }
  ]
  ```

### 📅 Timetable Management

#### Generate Timetable
- **POST** `/api/timetable/generate` - Generate optimized timetable
  ```json
  Response: {
    "message": "Timetable generated successfully with 85 entries",
    "entries_count": 85
  }
  ```

#### View Timetable
- **GET** `/api/timetable/view` - Get complete formatted timetable
  ```json
  Response: [
    {
      "course": "Programming 2",
      "lecturer": "Wanjiku Kamau",
      "department": "Information Technology and Computer Science",
      "day": "Monday",
      "start_time": "07:00",
      "end_time": "10:00",
      "room": "Computer Lab A",
      "year_level": 2,
      "requires_lab": true
    }
  ]
  ```

#### Validate Timetable
- **GET** `/api/timetable/validate` - Validate current timetable for conflicts
  ```json
  Response: {
    "is_valid": true,
    "conflicts": [],
    "warnings": []
  }
  ```

#### Filter by Department
- **GET** `/api/timetable/by-department/{department_code}` - Get timetable for specific department
  ```json
  Example: GET /api/timetable/by-department/ITCS
  Response: [/* Same format as /api/timetable/view but filtered */]
  ```

#### Filter by Lecturer
- **GET** `/api/timetable/by-lecturer/{lecturer_id}` - Get timetable for specific lecturer
  ```json
  Example: GET /api/timetable/by-lecturer/1
  Response: [/* Same format as /api/timetable/view but filtered */]
  ```

#### Conflict Analysis
- **GET** `/api/timetable/conflicts` - Get detailed conflict analysis
  ```json
  Response: {
    "conflicts": [
      {
        "type": "lecturer_conflict",
        "day": "Monday",
        "time": "07:00:00 - 10:00:00",
        "lecturer": "Wanjiku Kamau",
        "conflicting_units": ["Programming 2", "Database Systems"]
      }
    ]
  }
  ```

### 🔧 Debug Endpoints
- **GET** `/api/debug/data-check` - Check what data exists in database
- **POST** `/api/debug/regenerate-time-slots` - Regenerate time slots

## 🎨 Frontend Development Guide

### Data Models for Frontend

#### School Object
```typescript
interface School {
  id: number;
  name: string;
  code: string;
  created_at: string;
}
```

#### Department Object
```typescript
interface Department {
  id: number;
  name: string;
  code: string;
  school_id: number;
  created_at: string;
}
```

#### Lecturer Object
```typescript
interface Lecturer {
  id: number;
  name: string;
  employee_id: string;
  employment_type: 'full_time' | 'part_time';
  max_units: number;
  phone?: string;
  email?: string;
  created_at: string;
}
```

#### Unit Object
```typescript
interface Unit {
  id: number;
  name: string;
  code: string;
  department_id: number;
  year_level: number; // 1-4
  semester: number; // 1-2
  requires_lab: boolean;
  lecturer_id: number;
  created_at: string;
}
```

#### Room Object
```typescript
interface Room {
  id: number;
  name: string;
  capacity: number;
  room_type: 'normal' | 'lab';
  created_at: string;
}
```

#### TimetableEntry Object
```typescript
interface TimetableEntry {
  course: string;
  lecturer: string;
  department: string;
  day: 'Monday' | 'Tuesday' | 'Wednesday' | 'Thursday' | 'Friday';
  start_time: string; // HH:MM format
  end_time: string; // HH:MM format
  room: string;
  year_level: number;
  requires_lab: boolean;
}
```

### Recommended UI Components

#### 1. Dashboard Page
- **System Statistics Cards**: Display counts from `/api/statistics`
- **Quick Actions**: Initialize data, generate timetable, validate
- **Status Indicators**: Show if timetable exists, conflicts count

#### 2. Data Management Pages
- **Schools & Departments**: Table view with `/api/schools` and `/api/departments`
- **Lecturers**: Table with search/filter from `/api/lecturers`
- **Units/Courses**: Table with department filter from `/api/units`
- **Rooms**: Table with type filter from `/api/rooms`
- **Student Groups**: Table grouped by department from `/api/student-groups`

#### 3. Timetable Views
- **Grid View**: Weekly calendar grid using `/api/timetable/view`
- **Department Filter**: Dropdown to filter by department using `/api/timetable/by-department/{code}`
- **Lecturer View**: Individual lecturer schedules using `/api/timetable/by-lecturer/{id}`
- **Day View**: Single day detailed view
- **Room Utilization**: Show room bookings

#### 4. Timetable Management
- **Generate Button**: Call `/api/timetable/generate` with loading state
- **Validation Panel**: Show results from `/api/timetable/validate`
- **Conflict Resolution**: Display conflicts from `/api/timetable/conflicts`
- **Export Options**: PDF, Excel export functionality

### State Management Recommendations

#### API Client Setup
```typescript
const API_BASE_URL = 'http://localhost:8000';

// Generic API client
async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
}
```

#### Key API Functions
```typescript
// Data fetching
export const fetchSchools = () => apiCall<School[]>('/api/schools');
export const fetchDepartments = () => apiCall<Department[]>('/api/departments');
export const fetchLecturers = () => apiCall<Lecturer[]>('/api/lecturers');
export const fetchUnits = () => apiCall<Unit[]>('/api/units');
export const fetchRooms = () => apiCall<Room[]>('/api/rooms');
export const fetchTimetable = () => apiCall<TimetableEntry[]>('/api/timetable/view');
export const fetchStatistics = () => apiCall<Statistics>('/api/statistics');

// Timetable operations
export const generateTimetable = () => apiCall('/api/timetable/generate', { method: 'POST' });
export const validateTimetable = () => apiCall('/api/timetable/validate');
export const clearAllData = () => apiCall('/api/initialize/clear-all-data', { method: 'POST' });
export const initializeSampleData = () => apiCall('/api/initialize/sample-data', { method: 'POST' });

// Filtered views
export const fetchTimetableByDepartment = (code: string) => 
  apiCall<TimetableEntry[]>(`/api/timetable/by-department/${code}`);
export const fetchTimetableByLecturer = (id: number) => 
  apiCall<TimetableEntry[]>(`/api/timetable/by-lecturer/${id}`);
```

### Color Coding Suggestions

#### Department Colors
- **ITCS**: Blue (#3B82F6)
- **MAC**: Green (#10B981)
- **NURS**: Pink (#EC4899)
- **PSYC**: Purple (#8B5CF6)

#### Room Type Colors
- **Normal Rooms**: Light Gray (#F3F4F6)
- **Lab Rooms**: Orange (#F59E0B)

#### Time Slot Colors
- **Morning (7-10 AM)**: Light Blue
- **Mid-Morning (10-1 PM)**: Yellow
- **Afternoon (2-5 PM)**: Orange
- **Evening (5-7 PM)**: Red

### Error Handling

#### Common Error Scenarios
1. **500 Errors**: Database connection issues, constraint violations
2. **404 Errors**: Resource not found (lecturer, department, etc.)
3. **Network Errors**: API unavailable

#### Error Display
- Toast notifications for operations (generate, validate)
- Error boundaries for component crashes
- Loading states for all API calls
- Retry mechanisms for failed requests

### Performance Considerations

#### Optimization Tips
- Cache frequently accessed data (schools, departments)
- Implement pagination for large lists
- Use virtual scrolling for timetable grids
- Debounce search inputs
- Show loading skeletons

#### Real-time Updates
- Consider WebSocket integration for live timetable updates
- Refresh data after successful operations
- Show optimistic updates where appropriate

## 🏗️ System Architecture

### Database Schema
- **PostgreSQL** with SQLAlchemy ORM
- **Foreign Key Relationships** ensuring data integrity
- **Constraints** for data validation
- **Indexes** for performance optimization

### Business Logic
- **Constraint-based Scheduling**: Prevents lecturer/room/student conflicts
- **School-specific Time Slots**: SPAS (3-hour) vs SHS (2-hour) sessions
- **Lab Requirements**: Automatic lab room assignment for lab units
- **Load Balancing**: Distributes units across available time slots

### Time Slot System
- **SPAS Sessions** (3 hours): 7-10 AM, 10:30 AM-1:30 PM, 2-5 PM, 4-7 PM
- **SHS Sessions** (2 hours): 7-9 AM, 9-11 AM, 11 AM-1 PM, 2-4 PM, 4-6 PM, 5-7 PM
- **Monday to Friday** scheduling only
- **Break Times** automatically handled

## 🔒 API Security Notes
- All endpoints return JSON responses
- CORS enabled for frontend integration
- Error responses include detailed messages for debugging
- Input validation on all endpoints

This comprehensive guide should enable your frontend team to build a complete university timetable