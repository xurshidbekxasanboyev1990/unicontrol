# UniControl Mobile API Documentation

> **Base URL:** `https://unicontrol.uz/api/mobile`  
> **Auth:** Bearer Token (JWT) — get via `/api/mobile/auth/login`  
> **Version:** 2.0.0  
> **Last updated:** 2025-01-31

---

## Table of Contents

1. [Authentication](#1-authentication)
2. [Dashboard](#2-dashboard)
3. [Student Panel](#3-student-panel)
4. [Leader Panel](#4-leader-panel)
5. [Teacher Panel](#5-teacher-panel)
6. [Dean Panel](#6-dean-panel)
7. [Registrar Panel](#7-registrar-panel)
8. [Shared Modules](#8-shared-modules)
   - [Clubs](#81-clubs)
   - [Tournaments](#82-tournaments)
   - [Reports](#83-reports)
   - [Library](#84-library)
   - [Canteen](#85-canteen)
   - [Contracts](#86-contracts)
   - [Push Notifications](#87-push-notifications)
   - [Help/FAQ](#88-helpfaq)
   - [General](#89-general)

---

## Supported Mobile Roles

| Role | Prefix | Description |
|------|--------|-------------|
| `student` | `/student` | Student panel |
| `leader` | `/leader` | Group leader panel |
| `teacher` | `/teacher` | Teacher panel |
| `dean` | `/dean` | Dean (Dekanat) panel |
| `registrar_office` | `/registrar` | Registrar office panel |

> **Note:** `admin`, `superadmin`, and `academic_affairs` roles are **NOT** available on mobile. Admin/superadmin users will see the Dean dashboard on mobile.

---

## 1. Authentication

### POST `/auth/login`
Login and get JWT token.

**Request:**
```json
{
  "login": "string",
  "password": "string",
  "device_token": "string (optional, for push notifications)"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "login": "student001",
    "name": "Abdullayev Jasur",
    "role": "student",
    "avatar": null
  }
}
```

### GET `/auth/me`
Get current user info. **Requires: Bearer Token**

**Response:**
```json
{
  "id": 1,
  "login": "student001",
  "name": "Abdullayev Jasur",
  "role": "student",
  "email": "jasur@mail.com",
  "phone": "+998901234567",
  "avatar": null,
  "is_active": true
}
```

---

## 2. Dashboard

### GET `/dashboard/stats`
Unified dashboard endpoint — returns role-specific stats automatically.

**Requires:** Bearer Token

**Response varies by role:**

#### Student/Leader Response:
```json
{
  "role": "student",
  "total_students": 0,
  "total_groups": 0,
  "active_students": 0,
  "active_groups": 0,
  "today_present": 5,
  "today_absent": 1,
  "today_late": 0,
  "today_excused": 0,
  "today_attendance_rate": 83.3,
  "week_attendance_rate": 90.0,
  "month_attendance_rate": 88.5,
  "unread_notifications": 2,
  "today_lessons": 4,
  "pending_reports": 0
}
```

#### Teacher Response:
```json
{
  "role": "teacher",
  "total_groups": 5,
  "total_students": 120,
  "today_lessons": 3,
  "weekly_lessons": 18,
  "today_attendance_rate": 92.5,
  "unread_notifications": 1,
  "today_schedule": [
    {
      "id": 10,
      "subject": "Matematika",
      "group_name": "CS-21",
      "start_time": "08:00",
      "end_time": "09:20",
      "room": "301"
    }
  ]
}
```

#### Dean Response:
```json
{
  "role": "dean",
  "total_students": 1500,
  "total_groups": 45,
  "today_present": 1200,
  "today_absent": 150,
  "attendance_rate": 88.9,
  "today_lessons": 120,
  "nb_stats": { "total": 50, "active": 12, "approved": 30 },
  "contract_stats": { "total": 1500, "paid": 5000000.0, "debt": 2000000.0 }
}
```

#### Registrar Response:
```json
{
  "role": "registrar_office",
  "total_students": 1500,
  "total_groups": 45,
  "today_present": 1200,
  "today_absent": 150,
  "total_permits": 50,
  "active_permits": 12,
  "approved_permits": 30
}
```

---

## 3. Student Panel

### GET `/student/dashboard`
Student dashboard with attendance stats.

### GET `/student/schedule`
Student's weekly schedule.

### GET `/student/schedule/today`
Today's schedule only.

### GET `/student/attendance`
Student's attendance history.

| Param | Type | Description |
|-------|------|-------------|
| `date_from` | string | Start date (YYYY-MM-DD) |
| `date_to` | string | End date (YYYY-MM-DD) |

### GET `/student/grades`
Student's grades/marks.

### GET `/student/profile`
Student profile info.

### PUT `/student/profile`
Update profile (name, phone, email).

### POST `/student/change-password`
```json
{ "current_password": "old", "new_password": "new" }
```

---

## 4. Leader Panel

### GET `/leader/dashboard`
Leader dashboard with group stats.

### GET `/leader/group`
Leader's group info.

### GET `/leader/group/students`
Students in leader's group.

### GET `/leader/attendance`
Group attendance history.

### POST `/leader/attendance`
Mark attendance for group.

### GET `/leader/schedule`
Group's weekly schedule.

---

## 5. Teacher Panel

> **15 endpoints** — exact match with web v1/teacher

### GET `/teacher/dashboard`
Teacher dashboard statistics.

**Response:**
```json
{
  "total_groups": 5,
  "total_students": 120,
  "today_lessons": 3,
  "weekly_lessons": 18,
  "today_attendance_rate": 92.5,
  "today_schedule": [
    {
      "id": 1,
      "subject": "Matematika",
      "subject_code": "MAT101",
      "group_id": 10,
      "group_name": "CS-21",
      "start_time": "08:00",
      "end_time": "09:20",
      "time_range": "08:00-09:20",
      "room": "301",
      "lesson_number": 1,
      "week_type": "all",
      "schedule_type": "lecture"
    }
  ]
}
```

### GET `/teacher/schedule`
Full weekly schedule.

| Param | Type | Description |
|-------|------|-------------|
| `group_id` | int | Filter by group (optional) |

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "subject": "Matematika",
      "subject_code": "MAT101",
      "group_id": 10,
      "group_name": "CS-21",
      "day_of_week": "monday",
      "start_time": "08:00",
      "end_time": "09:20",
      "time_range": "08:00-09:20",
      "room": "301",
      "building": "A",
      "lesson_number": 1,
      "week_type": "all",
      "schedule_type": "lecture",
      "is_cancelled": false,
      "semester": 2,
      "academic_year": "2024-2025"
    }
  ],
  "total": 18
}
```

### GET `/teacher/schedule/today`
Today's schedule only.

### GET `/teacher/groups`
Teacher's assigned groups.

**Response:**
```json
{
  "items": [
    {
      "id": 10,
      "name": "CS-21",
      "faculty": "Kompyuter fanlari",
      "course_year": 2,
      "students_count": 25,
      "subjects": ["Matematika", "Fizika"],
      "is_active": true
    }
  ],
  "total": 5
}
```

### GET `/teacher/groups/{group_id}/students`
Students in a specific group with attendance rate.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Abdullayev Jasur",
      "full_name": "Abdullayev Jasur Bahodirovich",
      "hemis_id": "H12345",
      "student_id": "S001",
      "phone": "+998901234567",
      "email": "jasur@mail.com",
      "is_active": true,
      "attendance_rate": 88.5
    }
  ],
  "total": 25
}
```

### GET `/teacher/attendance`
Attendance history.

| Param | Type | Description |
|-------|------|-------------|
| `group_id` | int | Filter by group |
| `date_from` | string | Start date (YYYY-MM-DD) |
| `date_to` | string | End date (YYYY-MM-DD) |

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "student_id": 5,
      "student_name": "Abdullayev Jasur",
      "date": "2025-01-30",
      "status": "present",
      "subject": "Matematika",
      "lesson_number": 1,
      "note": "",
      "late_minutes": 0,
      "check_in_time": "08:05"
    }
  ],
  "total": 100
}
```

### POST `/teacher/attendance`
Batch mark attendance.

**Request:**
```json
{
  "group_id": 10,
  "date": "2025-01-30",
  "subject": "Matematika",
  "lesson_number": 1,
  "attendances": [
    { "student_id": 1, "status": "present", "note": "", "late_minutes": 0 },
    { "student_id": 2, "status": "absent", "note": "Kasal" },
    { "student_id": 3, "status": "late", "late_minutes": 15 }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Davomat saqlandi: 2 yangi, 1 yangilandi",
  "created": 2,
  "updated": 1
}
```

### GET `/teacher/attendance/summary`
Per-student attendance summary.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `group_id` | int | ✅ | Group ID |
| `date_from` | string | No | Start date |
| `date_to` | string | No | End date |

**Response:**
```json
{
  "group_id": 10,
  "date_from": "2025-01-01",
  "date_to": "2025-01-30",
  "students": [
    {
      "student_id": 1,
      "student_name": "Abdullayev Jasur",
      "hemis_id": "H12345",
      "total": 20,
      "present": 17,
      "absent": 2,
      "late": 1,
      "excused": 0,
      "rate": 90.0
    }
  ]
}
```

### GET `/teacher/profile`
Teacher profile.

### PUT `/teacher/profile`
Update teacher profile.
```json
{ "name": "string", "phone": "string", "email": "string" }
```

### POST `/teacher/change-password`
```json
{ "current_password": "old", "new_password": "new" }
```

### GET `/teacher/workload`
Search all workloads.

| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Teacher name search |
| `department` | string | Department filter |

### GET `/teacher/workload/my`
Teacher's own workload (auto-matched by name).

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "teacher_name": "Karimov Anvar",
      "department": "Informatika",
      "teacher_type": "штатный",
      "day_of_week": "monday",
      "day_name_uz": "Dushanba",
      "lesson_number": 1,
      "start_time": "08:00",
      "end_time": "09:20",
      "groups": "CS-21, CS-22",
      "is_busy": true
    }
  ],
  "total": 18,
  "teacher_name": "Karimov Anvar Olimovich",
  "search_name": "Karimov Anvar"
}
```

### GET `/teacher/workload/departments`
List of departments.

**Response:**
```json
{ "departments": ["Informatika", "Matematika", "Fizika"] }
```

### GET `/teacher/workload/teachers`
Teachers list with department info.

| Param | Type | Description |
|-------|------|-------------|
| `department` | string | Filter by department |

**Response:**
```json
{
  "teachers": [
    { "name": "Karimov Anvar", "department": "Informatika", "type": "штатный" }
  ],
  "total": 50
}
```

---

## 6. Dean Panel

> **14 endpoints** — exact match with web v1/dean

### GET `/dean/dashboard`
Dean dashboard statistics.

### GET `/dean/students`
Students list with filters.

| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Search by name/ID/phone |
| `group_id` | int | Filter by group |
| `faculty` | string | Filter by faculty |
| `course_year` | int | Filter by course |
| `page` | int | Page number (default: 1) |
| `per_page` | int | Items per page (default: 50) |

**Response:**
```json
{
  "items": [
    {
      "id": 1, "name": "Abdullayev Jasur",
      "student_id": "S001", "hemis_id": "H12345",
      "group_id": 10, "group_name": "CS-21",
      "phone": "+998901234567", "email": "jasur@mail.com",
      "passport": "AA1234567", "address": "Tashkent",
      "is_active": true,
      "contract_amount": 15000000.0, "contract_paid": 10000000.0
    }
  ],
  "total": 1500, "page": 1, "per_page": 50
}
```

### GET `/dean/faculties`
Distinct faculties list.

**Response:**
```json
{ "faculties": ["Kompyuter fanlari", "Iqtisodiyot", "Huquqshunoslik"] }
```

### GET `/dean/faculties-tree`
Faculty tree with groups and student counts.

**Response:**
```json
{
  "faculties": [
    {
      "name": "Kompyuter fanlari",
      "directions": [
        {
          "name": "Kompyuter fanlari",
          "groups": [
            { "id": 10, "name": "CS-21", "course_year": 2, "students_count": 25 }
          ],
          "groups_count": 3,
          "students_count": 75
        }
      ],
      "directions_count": 1, "groups_count": 3, "students_count": 75
    }
  ],
  "total_faculties": 5, "total_directions": 5, "total_groups": 45
}
```

### GET `/dean/groups`
Groups with filters.

| Param | Type | Description |
|-------|------|-------------|
| `faculty` | string | Filter by faculty |
| `course_year` | int | Filter by course |

### GET `/dean/attendance`
Attendance records.

| Param | Type | Description |
|-------|------|-------------|
| `date_val` | string | Single date (YYYY-MM-DD) |
| `date_from` | string | Range start |
| `date_to` | string | Range end |
| `group_id` | int | Filter by group |
| `status_filter` | string | present/absent/late/excused |

**Response:**
```json
{
  "items": [...],
  "stats": {
    "total": 100, "present": 80, "absent": 10, "late": 7, "excused": 3
  }
}
```

### GET `/dean/attendance/export`
Export attendance to Excel (.xlsx).

Same params as `/dean/attendance`. Returns binary Excel file.

### POST `/dean/attendance/import`
Import attendance from Excel.

**Request:** `multipart/form-data` with `file` field (.xlsx)

**Expected Excel columns:** `student_id`, `date`, `status`, `subject`, `lesson_number`

**Response:**
```json
{
  "success": true,
  "message": "Import tugallandi: 50 yangi, 10 yangilandi",
  "created": 50, "updated": 10,
  "errors": ["Qator 5: Talaba topilmadi (S999)"],
  "total_errors": 1
}
```

### GET `/dean/schedule`
Schedule with pagination.

| Param | Type | Description |
|-------|------|-------------|
| `group_id` | int | Filter by group |
| `faculty` | string | Filter by faculty |
| `course_year` | int | Filter by course |
| `teacher` | string | Search by teacher name |
| `page` | int | Page (default: 1) |
| `per_page` | int | Per page (default: 100) |

### GET `/dean/workload`
Teacher workload.

| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Teacher name search |
| `department` | string | Department filter |

### GET `/dean/workload/departments`
Departments list.

### GET `/dean/contracts/filters`
Contract filter options.

**Response:**
```json
{
  "faculties": ["Kompyuter fanlari"],
  "directions": ["Dasturiy injineriya"],
  "education_forms": ["kunduzgi", "sirtqi"],
  "courses": ["1", "2", "3", "4"],
  "academic_years": ["2024-2025"]
}
```

### GET `/dean/contracts`
Contracts list with full stats.

| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Student name/ID search |
| `group_id` | int | Filter by group |
| `faculty` | string | Faculty filter |
| `direction` | string | Direction filter |
| `course` | string | Course filter |
| `education_form` | string | Education form |
| `academic_year` | string | Academic year |
| `has_debt` | bool | true=with debt only |
| `page` | int | Page (default: 1) |
| `per_page` | int | Per page (default: 50) |

**Response:**
```json
{
  "items": [
    {
      "id": 1, "student_name": "Abdullayev Jasur",
      "student_id_number": "12345678901234",
      "group_name": "CS-21", "direction": "Dasturiy injineriya",
      "course": "2", "education_form": "kunduzgi",
      "contract_amount": 15000000.0, "paid_amount": 10000000.0,
      "debt": 5000000.0, "is_paid": false,
      "academic_year": "2024-2025", "grant_percentage": 0.0
    }
  ],
  "total": 1500,
  "stats": {
    "total": 1500, "paid": 800, "unpaid": 700,
    "total_contract_amount": 22500000000.0,
    "total_paid": 15000000000.0,
    "total_debt": 7500000000.0,
    "payment_percentage": 66.7
  }
}
```

### GET `/dean/nb-permits`
NB permits (read-only).

| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Search by code/subject/student |
| `status_filter` | string | Filter by status |

---

## 7. Registrar Panel

> **17 endpoints** — exact match with web v1/registrar

### GET `/registrar/dashboard`
Registrar dashboard.

### GET `/registrar/faculties`
Faculties with student counts.

**Response:**
```json
{
  "faculty_counts": [
    { "name": "Kompyuter fanlari", "students_count": 500 }
  ],
  "course_years": [1, 2, 3, 4]
}
```

### GET `/registrar/students`
Students list with full details.

| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Name/ID/phone/passport search |
| `group_id` | int | Filter by group |
| `faculty` | string | Faculty filter |
| `course_year` | int | Course filter |
| `page` | int | Page (default: 1) |
| `limit` | int | Per page (default: 50) |

**Response:**
```json
{
  "items": [
    {
      "id": 1, "student_id": "S001", "name": "Abdullayev Jasur",
      "phone": "+998901234567", "email": "jasur@mail.com",
      "passport": "AA1234567", "jshshir": "12345678901234",
      "birth_date": "2003-05-15", "gender": "male",
      "group_id": 10, "group_name": "CS-21",
      "faculty": "Kompyuter fanlari", "course_year": 2,
      "contract_amount": 15000000.0, "contract_paid": 10000000.0,
      "enrollment_date": "2023-09-01", "is_active": true
    }
  ],
  "total": 1500, "page": 1, "limit": 50
}
```

### GET `/registrar/students/{student_id}`
Student full details with permits and attendance stats.

**Response:**
```json
{
  "student": {
    "id": 1, "student_id": "S001", "name": "Abdullayev Jasur",
    "phone": "+998901234567", "email": "jasur@mail.com",
    "passport": "AA1234567", "jshshir": "12345678901234",
    "birth_date": "2003-05-15", "gender": "male", "address": "Tashkent",
    "group_id": 10, "group_name": "CS-21",
    "faculty": "Kompyuter fanlari", "course_year": 2,
    "contract_amount": 15000000.0, "contract_paid": 10000000.0,
    "enrollment_date": "2023-09-01", "is_active": true
  },
  "attendance": {
    "total_days": 100, "present_days": 85, "absent_days": 15,
    "attendance_rate": 85.0
  },
  "permits": [
    {
      "id": 1, "permit_code": "NB-2025-001",
      "subject_name": "Matematika", "semester": 1,
      "academic_year": "2024-2025", "nb_type": "nb",
      "status": "issued", "teacher_name": "Karimov Anvar",
      "issue_date": "2025-01-15", "expiry_date": "2025-02-15",
      "completed_date": null, "result_grade": null,
      "created_at": "2025-01-15T10:30:00"
    }
  ]
}
```

### GET `/registrar/attendance`
Attendance records (read-only).

| Param | Type | Description |
|-------|------|-------------|
| `date_val` | date | Single date |
| `date_from` | date | Range start |
| `date_to` | date | Range end |
| `group_id` | int | Filter by group |
| `status_filter` | string | present/absent/late/excused |
| `page` | int | Page (default: 1) |
| `limit` | int | Per page (default: 100) |

### GET `/registrar/permits`
All NB permits with pagination.

| Param | Type | Description |
|-------|------|-------------|
| `status_filter` | string | issued/pending/in_progress/approved/rejected/cancelled |
| `student_id` | int | Filter by student |
| `search` | string | Search by code/subject |
| `page` | int | Page (default: 1) |
| `limit` | int | Per page (default: 50) |

**Response:**
```json
{
  "items": [
    {
      "id": 1, "permit_code": "NB-2025-001",
      "student_id": 1, "student_name": "Abdullayev Jasur",
      "student_sid": "S001", "group_name": "CS-21",
      "subject_name": "Matematika", "semester": 1,
      "academic_year": "2024-2025", "nb_type": "nb",
      "reason": "Kasal bo'lgan", "teacher_id": 5,
      "teacher_name": "Karimov Anvar", "issued_by_name": "Registrator",
      "issue_date": "2025-01-15", "expiry_date": "2025-02-15",
      "completed_date": null,
      "status": "issued", "result_grade": null,
      "teacher_notes": null, "registrar_notes": "Tibbiy spravka bor",
      "print_count": 0, "created_at": "2025-01-15T10:30:00"
    }
  ],
  "total": 50, "page": 1, "limit": 50
}
```

### POST `/registrar/permits`
Create new NB permit.

**Request:**
```json
{
  "student_id": 1,
  "subject_name": "Matematika",
  "semester": 1,
  "academic_year": "2024-2025",
  "nb_type": "nb",
  "reason": "Kasal bo'lgan",
  "teacher_id": 5,
  "teacher_name": "Karimov Anvar",
  "expiry_date": "2025-02-15",
  "registrar_notes": "Tibbiy spravka bor"
}
```

**Response:**
```json
{
  "id": 1,
  "permit_code": "NB-2025-001",
  "status": "issued",
  "message": "Ruxsatnoma muvaffaqiyatli yaratildi"
}
```

### PUT `/registrar/permits/{permit_id}`
Update permit.

**Request:**
```json
{
  "status": "approved",
  "result_grade": "4",
  "teacher_notes": "Yaxshi topshirdi",
  "registrar_notes": "Tasdiqlandi"
}
```

### DELETE `/registrar/permits/{permit_id}`
Delete/cancel permit.

### GET `/registrar/permits/{permit_id}/check`
Get permit receipt for printing. **Increments print count.**

**Response:**
```json
{
  "permit_code": "NB-2025-001",
  "is_valid": true,
  "student": {
    "name": "Abdullayev Jasur",
    "student_id": "S001",
    "group_name": "CS-21",
    "faculty": "Kompyuter fanlari"
  },
  "subject_name": "Matematika",
  "semester": 1,
  "academic_year": "2024-2025",
  "nb_type": "nb",
  "reason": "Kasal bo'lgan",
  "teacher_name": "Karimov Anvar",
  "issued_by_name": "Registrator",
  "issue_date": "2025-01-15",
  "expiry_date": "2025-02-15",
  "completed_date": null,
  "status": "issued",
  "result_grade": null,
  "teacher_notes": null,
  "print_count": 1,
  "verification_hash": "a1b2c3d4e5f6g7h8..."
}
```

### GET `/registrar/verify/{permit_code}`
Verify permit by code (public-accessible).

**Response:**
```json
{
  "valid": true,
  "permit_code": "NB-2025-001",
  "student_name": "Abdullayev Jasur",
  "subject_name": "Matematika",
  "status": "issued",
  "issue_date": "2025-01-15",
  "result_grade": null,
  "is_approved": false
}
```

### GET `/registrar/teacher-permits`
Permits assigned to current teacher. **Requires: Teacher role**

| Param | Type | Description |
|-------|------|-------------|
| `status_filter` | string | Filter by status |

### PUT `/registrar/teacher-permits/{permit_id}`
Teacher approve/reject permit. **Requires: Teacher role**

**Request:**
```json
{
  "status": "approved",
  "result_grade": "5",
  "teacher_notes": "A'lo topshirdi"
}
```

### GET `/registrar/groups`
All active groups (for dropdown).

### GET `/registrar/teachers`
All teachers (for permit assignment dropdown).

**Response:**
```json
{
  "items": [
    { "id": 5, "name": "Karimov Anvar" }
  ]
}
```

### GET `/registrar/my-permits`
Student's own NB permits. **Requires: Student/Leader role**

### GET `/registrar/group-permits`
Leader's group permits. **Requires: Leader role**

---

## 8. Shared Modules

### 8.1 Clubs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/clubs` | List all clubs |
| GET | `/clubs/{id}` | Club details |

### 8.2 Tournaments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tournaments` | List tournaments |
| GET | `/tournaments/{id}` | Tournament details |

### 8.3 Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports` | List reports |
| POST | `/reports` | Submit report |

### 8.4 Library
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/library/books` | Search books |
| GET | `/library/my-books` | My borrowed books |

### 8.5 Canteen
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/canteen/menu` | Today's menu |

### 8.6 Contracts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/contracts/my` | My contract info |

### 8.7 Push Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/push/register` | Register device token |
| DELETE | `/push/unregister` | Unregister device |

### 8.8 Help/FAQ
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/help/faq` | Frequently asked questions |
| POST | `/help/contact` | Send support message |

### 8.9 General
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/schedule` | Universal schedule |
| GET | `/attendance` | Universal attendance |
| GET | `/groups` | All groups |
| GET | `/notifications/unread-count` | Unread notification count |

---

## Error Responses

All endpoints return standard error format:

```json
{
  "detail": "Error message in Uzbek"
}
```

| Status Code | Description |
|-------------|-------------|
| 400 | Bad request (invalid params) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (wrong role) |
| 404 | Not found |
| 422 | Validation error |
| 500 | Server error |

---

## Attendance Status Values

| Value | Uzbek | Description |
|-------|-------|-------------|
| `present` | Kelgan | Student is present |
| `absent` | Kelmagan | Student is absent |
| `late` | Kechikkan | Student arrived late |
| `excused` | Sababli | Excused absence |

## NB Permit Status Values

| Value | Description |
|-------|-------------|
| `issued` | Newly issued |
| `pending` | Pending review |
| `in_progress` | In progress |
| `approved` | Approved by teacher |
| `rejected` | Rejected by teacher |
| `cancelled` | Cancelled |

---

## Endpoint Count Summary

| Panel | Endpoints | Match with Web |
|-------|-----------|----------------|
| Teacher | 15 | ✅ 100% match |
| Dean | 14 | ✅ 100% match |
| Registrar | 17 | ✅ 100% match |
| Student | ~8 | ✅ Full panel |
| Leader | ~6 | ✅ Full panel |
| **Total unique** | **~60+** | |
