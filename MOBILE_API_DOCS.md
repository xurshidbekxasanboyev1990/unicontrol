# 📱 UniControl Mobile API — To'liq Dokumentatsiya

> **Versiya:** 2.0.0  
> **Base URL:** `https://unicontrol.uz/api/mobile`  
> **Backend:** FastAPI + PostgreSQL  
> **Mobile App:** Flutter (Dart) + Riverpod  
> **Autentifikatsiya:** JWT Bearer Token  
> **Sanasi:** 2026-02-18

---

## 📋 Mundarija

1. [Arxitektura](#-arxitektura)
2. [Rollar va Panellar](#-rollar-va-panellar)
3. [Autentifikatsiya](#-autentifikatsiya)
4. [Mobile App Ekranlari](#-mobile-app-ekranlari)
5. [API Endpointlar — To'liq Ro'yxat](#-api-endpointlar--toliq-royxat)
   - [Auth](#1-auth--autentifikatsiya)
   - [Dashboard](#2-dashboard)
   - [Student](#3-student--talaba)
   - [Leader](#4-leader--sardor)
   - [General](#5-general--umumiy)
   - [Clubs](#6-clubs--togaraklar)
   - [Tournaments](#7-tournaments--turnirlar)
   - [Reports](#8-reports--hisobotlar)
   - [Library](#9-library--kutubxona)
   - [Canteen](#10-canteen--oshxona)
   - [Contracts](#11-contracts--kontraktlar)
   - [Help/FAQ](#12-helpfaq)
   - [Push Notifications](#13-push-notifications)
6. [Web Panellar va API v1](#-web-panellar-va-api-v1)
7. [Data Modellar](#-data-modellar)
8. [Xatolar va Status Kodlar](#-xatolar-va-status-kodlar)

---

## 🏗 Arxitektura

```
┌──────────────────────────────────────────────────────────────┐
│                      UNICONTROL SYSTEM                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │  Mobile App  │    │   Web App   │    │  Telegram Bot   │  │
│  │  (Flutter)   │    │  (Vue 3)    │    │  (aiogram)      │  │
│  └──────┬───────┘    └──────┬──────┘    └───────┬─────────┘  │
│         │                   │                   │            │
│         ▼                   ▼                   ▼            │
│  /api/mobile/*       /api/v1/*           /api/v1/telegram/*  │
│         │                   │                   │            │
│         └───────────┬───────┘───────────────────┘            │
│                     ▼                                        │
│            ┌─────────────────┐                               │
│            │  FastAPI Server  │                               │
│            │  (Uvicorn)       │                               │
│            └────────┬────────┘                               │
│                     ▼                                        │
│            ┌─────────────────┐                               │
│            │   PostgreSQL     │                               │
│            │   Database       │                               │
│            └─────────────────┘                               │
│                                                              │
│  Docker Compose: nginx + backend + frontend + postgres + bot │
└──────────────────────────────────────────────────────────────┘
```

### URL Tuzilishi

| Platforma | Base URL | Tavsif |
|-----------|----------|--------|
| Mobile API | `/api/mobile/*` | Flutter mobil ilova uchun |
| Web API v1 | `/api/v1/*` | Vue.js web panel uchun |
| Web API (alias) | `/api/*` | `/api/v1` bilan bir xil (frontend mos) |
| Health Check | `/health` | Load balancer uchun |

---

## 👥 Rollar va Panellar

### Foydalanuvchi Rollari

| Rol | Qiymat | Tavsif | Ruxsatlar |
|-----|--------|--------|-----------|
| **Talaba** | `student` | Oddiy talaba | O'z ma'lumotlarini ko'rish, davomat, jadval |
| **Sardor** | `leader` | Guruh rahbari (starosta) | Talaba + davomat belgilash, hisobot, guruh boshqaruvi |
| **Admin** | `admin` | O'quv muassasa admini | Barcha boshqaruv: talabalar, guruhlar, jadval, import |
| **Super Admin** | `superadmin` | Tizim super admini | BARCHA ruxsatlar + tizim sozlamalari, loglar, adminlar |

### Mobile App — Rolga qarab ko'rinadigan funksiyalar

| Funksiya | Student | Leader | Admin | SuperAdmin |
|----------|---------|--------|-------|------------|
| Dashboard | ✅ | ✅ | ✅ | ✅ |
| Davomat ko'rish | ✅ | ✅ | ✅ | ✅ |
| Davomat belgilash | ❌ | ✅ | ❌ | ❌ |
| Jadval | ✅ | ✅ | ✅ | ✅ |
| Bildirishnomalar | ✅ | ✅ | ✅ | ✅ |
| Profil | ✅ | ✅ | ✅ | ✅ |
| Talabalar ro'yxati | ❌ | ✅ | ✅ | ✅ |
| Guruhlar | ❌ | ❌ | ✅ | ✅ |
| Hisobotlar | ❌ | ✅ | ✅ | ✅ |
| To'garaklar | ✅ | ✅ | ✅ | ✅ |
| Turnirlar | ✅ | ✅ | ✅ | ✅ |
| Kutubxona | ✅ | ✅ | ✅ | ✅ |
| Oshxona | ✅ | ✅ | ✅ | ✅ |
| Kontraktlar | ✅ | ✅ | ❌ | ❌ |
| Yordam/FAQ | ✅ | ✅ | ✅ | ✅ |
| Sozlamalar | ✅ | ✅ | ✅ | ✅ |

---

## 🔐 Autentifikatsiya

**Metod:** JWT Bearer Token  
**Header:** `Authorization: Bearer <access_token>`

### Token Oqimi

```
1. POST /auth/login  →  {access_token, refresh_token}
2. Har bir so'rovda:  Authorization: Bearer <access_token>
3. Token eskirganda:  POST /auth/refresh  →  yangi tokenlar
4. Chiqish:  POST /auth/logout  →  refresh_token bekor qilinadi
```

### Token Ma'lumotlari

| Maydon | Tavsif |
|--------|--------|
| `access_token` | Qisqa muddatli (15-30 min), API so'rovlar uchun |
| `refresh_token` | Uzoq muddatli, yangi access_token olish uchun |
| `token_type` | Doimo `"bearer"` |

---

## 📲 Mobile App Ekranlari

Flutter mobil ilovadagi barcha ekranlar:

| # | Ekran | Route | Fayl | Tavsif |
|---|-------|-------|------|--------|
| 1 | Splash | `/splash` | `auth/screens/splash_screen.dart` | Ilova yuklanishi, token tekshirish |
| 2 | Login | `/login` | `auth/screens/login_screen.dart` | Login va parol bilan kirish |
| 3 | Dashboard | `/dashboard` | `dashboard/screens/dashboard_screen.dart` | Asosiy panel (rolga qarab) |
| 4 | Davomat | `/attendance` | `attendance/screens/attendance_screen.dart` | Davomat tarixi |
| 5 | Davomat belgilash | `/attendance/mark` | `attendance/screens/mark_attendance_screen.dart` | Leader: davomat belgilash |
| 6 | Jadval | `/schedule` | `schedule/screens/schedule_screen.dart` | Haftalik dars jadvali |
| 7 | Profil | `/profile` | `profile/screens/profile_screen.dart` | Shaxsiy ma'lumotlar |
| 8 | Talabalar | `/students` | `students/screens/students_screen.dart` | Talabalar ro'yxati |
| 9 | Talaba info | `/students/:id` | `students/screens/student_detail_screen.dart` | Talaba batafsil |
| 10 | Guruhlar | `/groups` | `groups/screens/groups_screen.dart` | Guruhlar ro'yxati |
| 11 | Guruh info | `/groups/:id` | `groups/screens/group_detail_screen.dart` | Guruh batafsil |
| 12 | Bildirishnomalar | `/notifications` | `notifications/screens/notifications_screen.dart` | Xabarlar |
| 13 | Xabar yozish | `/notifications/compose` | `notifications/screens/notification_compose_screen.dart` | Leader: xabar yuborish |
| 14 | Hisobotlar | `/reports` | `reports/screens/reports_screen.dart` | Hisobotlar |
| 15 | To'garaklar | `/clubs` | `clubs/screens/clubs_screen.dart` | To'garaklar |
| 16 | Turnirlar | `/tournaments` | `tournaments/screens/tournaments_screen.dart` | Turnirlar |
| 17 | Sozlamalar | `/settings` | `settings/screens/settings_screen.dart` | Ilova sozlamalari |
| 18 | Kutubxona | `/library` | `library/screens/library_screen.dart` | Kitoblar |
| 19 | Oshxona | `/canteen` | `canteen/screens/canteen_screen.dart` | Taomlar va buyurtma |
| 20 | Kontraktlar | `/contracts` | `contracts/screens/contracts_screen.dart` | Kontrakt to'lovlari |
| 21 | Yordam | `/help` | `help/screens/help_screen.dart` | FAQ va yordam |

### Bottom Navigation (MainShell)

```
┌────────┬────────────┬──────────┬──────────┐
│  🏠    │  📋       │  📅      │  👤      │
│ Bosh   │ Davomat   │ Jadval   │ Profil   │
│ sahifa │           │          │          │
└────────┴────────────┴──────────┴──────────┘
```

---

## 📡 API Endpointlar — To'liq Ro'yxat

### 1. Auth — Autentifikatsiya

**Prefix:** `/api/mobile/auth`

| # | Metod | Endpoint | Auth | Tavsif |
|---|-------|----------|------|--------|
| 1 | `POST` | `/auth/login` | ❌ | Tizimga kirish |
| 2 | `POST` | `/auth/refresh` | ❌ | Token yangilash |
| 3 | `POST` | `/auth/logout` | ✅ | Tizimdan chiqish |
| 4 | `POST` | `/auth/register-device` | ✅ | Push token ro'yxatdan o'tkazish |
| 5 | `GET` | `/auth/me` | ✅ | Joriy foydalanuvchi ma'lumotlari |
| 6 | `PUT/POST` | `/auth/change-password` | ✅ | Parol o'zgartirish |

#### 1.1 `POST /auth/login`

**Request:**
```json
{
  "username": "12345",
  "password": "parol123",
  "device_token": "firebase_token_here",
  "device_type": "android"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJI...",
  "refresh_token": "eyJhbGciOiJI...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "login": "12345",
    "email": "student@mail.uz",
    "name": "Aliyev Ali",
    "role": "student",
    "avatar": "/uploads/avatar.jpg",
    "phone": "+998901234567",
    "group_id": 10,
    "group_name": "MT-21"
  }
}
```

#### 1.2 `POST /auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJI..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJI_yangi...",
  "refresh_token": "eyJhbGciOiJI_yangi...",
  "token_type": "bearer"
}
```

#### 1.3 `GET /auth/me`

**Response (200):**
```json
{
  "id": 1,
  "login": "12345",
  "email": "student@mail.uz",
  "name": "Aliyev Ali",
  "role": "student",
  "avatar": "/uploads/avatar.jpg",
  "phone": "+998901234567",
  "is_active": true,
  "group_id": 10,
  "group_name": "MT-21"
}
```

#### 1.4 `PUT /auth/change-password`

**Request:**
```json
{
  "current_password": "eski_parol",
  "new_password": "yangi_parol"
}
```

---

### 2. Dashboard

**Prefix:** `/api/mobile/dashboard`

| # | Metod | Endpoint | Auth | Rol | Tavsif |
|---|-------|----------|------|-----|--------|
| 1 | `GET` | `/dashboard/stats` | ✅ | Hammasi | Rolga qarab dashboard statistikasi |

#### 2.1 `GET /dashboard/stats`

Rolga qarab turli ma'lumot qaytaradi:

**Student uchun Response:**
```json
{
  "role": "student",
  "total_students": 0,
  "total_groups": 0,
  "active_students": 0,
  "active_groups": 0,
  "today_present": 1,
  "today_absent": 0,
  "today_late": 0,
  "today_excused": 0,
  "today_attendance_rate": 85.5,
  "week_attendance_rate": 90.2,
  "month_attendance_rate": 87.3,
  "unread_notifications": 3,
  "today_lessons": 4,
  "pending_reports": 0
}
```

**Leader uchun Response:**
```json
{
  "role": "leader",
  "total_students": 25,
  "total_groups": 1,
  "active_students": 25,
  "active_groups": 1,
  "today_present": 20,
  "today_absent": 3,
  "today_late": 2,
  "today_excused": 0,
  "today_attendance_rate": 80.0,
  "week_attendance_rate": 85.5,
  "month_attendance_rate": 82.1,
  "unread_notifications": 5,
  "today_lessons": 6,
  "pending_reports": 0
}
```

**Admin/SuperAdmin uchun Response:**
```json
{
  "role": "admin",
  "total_students": 500,
  "total_groups": 20,
  "active_students": 480,
  "active_groups": 18,
  "today_present": 400,
  "today_absent": 50,
  "today_late": 20,
  "today_excused": 10,
  "today_attendance_rate": 83.3,
  "week_attendance_rate": 85.0,
  "month_attendance_rate": 84.2,
  "unread_notifications": 12,
  "pending_reports": 3,
  "today_lessons": 0
}
```

---

### 3. Student — Talaba

**Prefix:** `/api/mobile/student`

| # | Metod | Endpoint | Auth | Rol | Tavsif |
|---|-------|----------|------|-----|--------|
| 1 | `GET` | `/student/profile` | ✅ | Student | Talaba profili |
| 2 | `GET` | `/student/dashboard` | ✅ | Student | Talaba dashboardi |
| 3 | `GET` | `/student/attendance` | ✅ | Student | Davomat tarixi |
| 4 | `GET` | `/student/schedule/today` | ✅ | Student | Bugungi jadval |
| 5 | `GET` | `/student/schedule/week` | ✅ | Student | Haftalik jadval |
| 6 | `GET` | `/student/notifications` | ✅ | Student | Bildirishnomalar |
| 7 | `POST` | `/student/notifications/{id}/read` | ✅ | Student | O'qildi belgilash |

#### 3.1 `GET /student/profile`

```json
{
  "id": 1,
  "full_name": "Aliyev Ali Valiyevich",
  "hemis_id": "12345678",
  "email": "ali@mail.uz",
  "phone": "+998901234567",
  "group_id": 10,
  "group_name": "MT-21",
  "contract_amount": 12000000.0,
  "contract_paid": 8000000.0,
  "avatar": "/uploads/avatar.jpg"
}
```

#### 3.2 `GET /student/dashboard`

```json
{
  "student_name": "Aliyev Ali",
  "today_status": "present",
  "attendance_rate": 87.5,
  "today_classes": 4,
  "unread_notifications": 2
}
```

`today_status` qiymatlari: `"present"`, `"absent"`, `"late"`, `"excused"`, `"not_marked"`

#### 3.3 `GET /student/attendance?days=30`

**Query params:**

| Param | Tur | Default | Tavsif |
|-------|-----|---------|--------|
| `days` | int | 30 | Necha kunlik tarix (1-90) |

```json
{
  "records": [
    {
      "date": "2026-02-18",
      "status": "present",
      "notes": null
    },
    {
      "date": "2026-02-17",
      "status": "absent",
      "notes": "Kasallik"
    }
  ],
  "stats": {
    "total": 20,
    "present": 17,
    "absent": 2,
    "late": 1
  }
}
```

#### 3.4 `GET /student/schedule/today`

```json
{
  "date": "2026-02-18",
  "day": "TUESDAY",
  "classes": [
    {
      "id": 1,
      "subject": "Matematika",
      "start_time": "09:00",
      "end_time": "10:20",
      "room": "301",
      "teacher": "Karimov B.S."
    }
  ]
}
```

#### 3.5 `GET /student/schedule/week`

```json
{
  "MONDAY": [
    {"id": 1, "subject": "Fizika", "start_time": "08:00", "end_time": "09:20", "room": "201", "teacher": "Nazarov T."}
  ],
  "TUESDAY": [...],
  "WEDNESDAY": [...],
  "THURSDAY": [...],
  "FRIDAY": [...],
  "SATURDAY": []
}
```

#### 3.6 `GET /student/notifications?page=1&page_size=20`

```json
{
  "notifications": [
    {
      "id": 1,
      "title": "Jadval o'zgarishi",
      "message": "Ertangi darslar 9:00 dan boshlanadi",
      "type": "info",
      "is_read": false,
      "created_at": "2026-02-18T10:30:00"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

---

### 4. Leader — Sardor

**Prefix:** `/api/mobile/leader`

| # | Metod | Endpoint | Auth | Rol | Tavsif |
|---|-------|----------|------|-----|--------|
| 1 | `GET` | `/leader/dashboard` | ✅ | Leader | Sardor dashboardi |
| 2 | `GET` | `/leader/students` | ✅ | Leader | Guruh talabalari |
| 3 | `GET` | `/leader/attendance/today` | ✅ | Leader | Bugungi davomat holati |
| 4 | `POST` | `/leader/attendance/quick` | ✅ | Leader | Tez davomat belgilash (1 ta) |
| 5 | `POST` | `/leader/attendance/bulk` | ✅ | Leader | Ko'p davomat belgilash |
| 6 | `GET` | `/leader/schedule/today` | ✅ | Leader | Bugungi jadval |
| 7 | `GET` | `/leader/stats/week` | ✅ | Leader | Haftalik statistika |
| 8 | `POST` | `/leader/send-notification` | ✅ | Leader | Guruhga xabar yuborish |

#### 4.1 `GET /leader/dashboard`

```json
{
  "group": {
    "id": 10,
    "name": "MT-21",
    "code": "MT21"
  },
  "students_count": 25,
  "today_attendance": {
    "marked": 20,
    "not_marked": 5,
    "present": 18,
    "absent": 2
  },
  "today_classes": 6
}
```

#### 4.2 `GET /leader/students`

```json
[
  {
    "id": 1,
    "full_name": "Aliyev Ali Valiyevich",
    "hemis_id": "12345678",
    "phone": "+998901234567"
  }
]
```

#### 4.3 `GET /leader/attendance/today`

```json
{
  "date": "2026-02-18",
  "students": [
    {
      "id": 1,
      "full_name": "Aliyev Ali",
      "status": "present",
      "notes": null
    },
    {
      "id": 2,
      "full_name": "Karimova Dilnoza",
      "status": null,
      "notes": null
    }
  ]
}
```

`status: null` = hali belgilanmagan

#### 4.4 `POST /leader/attendance/quick`

**Request:**
```json
{
  "student_id": 1,
  "status": "present"
}
```

`status` qiymatlari: `"present"`, `"absent"`, `"late"`, `"excused"`

**Response (200):**
```json
{
  "message": "Attendance marked",
  "status": "present"
}
```

#### 4.5 `POST /leader/attendance/bulk`

**Request:**
```json
{
  "attendance_date": "2026-02-18",
  "records": [
    {"student_id": 1, "status": "present"},
    {"student_id": 2, "status": "absent"},
    {"student_id": 3, "status": "late"}
  ]
}
```

**Response (200):**
```json
{
  "marked": 3,
  "errors": []
}
```

#### 4.6 `GET /leader/stats/week`

```json
{
  "week_start": "2026-02-16",
  "daily_stats": [
    {
      "date": "2026-02-16",
      "total": 25,
      "present": 22,
      "absent": 3,
      "rate": 88.0
    }
  ]
}
```

#### 4.7 `POST /leader/send-notification?title=...&message=...`

**Query params:**

| Param | Tur | Tavsif |
|-------|-----|--------|
| `title` | string | Xabar sarlavhasi |
| `message` | string | Xabar matni |

```json
{
  "message": "Sent 25 notifications"
}
```

---

### 5. General — Umumiy

**Prefix:** `/api/mobile` (prefiksiz)

Bu endpointlar barcha rollar uchun ishlaydi.

| # | Metod | Endpoint | Auth | Tavsif |
|---|-------|----------|------|--------|
| **Jadval** | | | | |
| 1 | `GET` | `/schedule` | ✅ | Jadval (filtrlash bilan) |
| 2 | `GET` | `/schedule/today` | ✅ | Bugungi jadval |
| 3 | `GET` | `/schedule/week` | ✅ | Haftalik jadval |
| **Davomat** | | | | |
| 4 | `GET` | `/attendance` | ✅ | Davomat yozuvlari (filtrlash) |
| 5 | `POST` | `/attendance/batch` | ✅ (Leader) | Ko'plik davomat belgilash |
| 6 | `GET` | `/attendance/stats` | ✅ | Davomat statistikasi |
| **Guruhlar** | | | | |
| 7 | `GET` | `/groups` | ✅ | Guruhlar ro'yxati |
| 8 | `GET` | `/groups/{id}` | ✅ | Guruh batafsil |
| 9 | `GET` | `/groups/{id}/students` | ✅ | Guruh talabalari |
| **Talabalar** | | | | |
| 10 | `GET` | `/students` | ✅ | Talabalar ro'yxati |
| 11 | `GET` | `/students/{id}` | ✅ | Talaba batafsil |
| **Bildirishnomalar** | | | | |
| 12 | `GET` | `/notifications` | ✅ | Bildirishnomalar |
| 13 | `GET` | `/notifications/unread-count` | ✅ | O'qilmagan soni |
| 14 | `PUT/POST` | `/notifications/{id}/read` | ✅ | O'qildi belgilash |
| 15 | `PUT/POST` | `/notifications/read-all` | ✅ | Barchasini o'qildi |

#### 5.1 `GET /schedule`

**Query params:**

| Param | Tur | Tavsif |
|-------|-----|--------|
| `group_id` | int? | Guruh ID (opsional, avtomatik aniqlanadi) |
| `day` | string? | Kun nomi: `monday`, `tuesday`, ... |

```json
{
  "schedule": [
    {
      "id": 1,
      "subject": "Matematika",
      "start_time": "09:00",
      "end_time": "10:20",
      "room": "301",
      "teacher": "Karimov B.S.",
      "day_of_week": "MONDAY",
      "day": "MONDAY",
      "is_cancelled": false
    }
  ]
}
```

#### 5.2 `GET /schedule/week`

```json
{
  "week_start": "2026-02-16",
  "days": [
    {
      "day": "MONDAY",
      "date": "2026-02-16",
      "classes": [...]
    },
    {
      "day": "TUESDAY",
      "date": "2026-02-17",
      "classes": [...]
    }
  ]
}
```

#### 5.3 `GET /attendance`

**Query params:**

| Param | Tur | Default | Tavsif |
|-------|-----|---------|--------|
| `student_id` | int? | - | Talaba ID |
| `group_id` | int? | - | Guruh ID |
| `date_from` | string? | - | Boshlanish sanasi (YYYY-MM-DD) |
| `date_to` | string? | - | Tugash sanasi (YYYY-MM-DD) |
| `days` | int | 30 | Necha kunlik (1-365) |
| `status` | string? | - | Filter: present/absent/late/excused |
| `page` | int | 1 | Sahifa |
| `page_size` | int | 50 | Sahifa hajmi (1-200) |

```json
{
  "items": [
    {
      "id": 1,
      "student_id": 5,
      "student_name": null,
      "group_id": null,
      "date": "2026-02-18",
      "status": "present",
      "reason": null,
      "notes": null,
      "marked_by": 100,
      "created_at": "2026-02-18T09:00:00"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 50
}
```

#### 5.4 `GET /attendance/stats`

**Query params:** `student_id`, `group_id`, `days` (default: 30)

```json
{
  "total": 20,
  "present": 17,
  "absent": 2,
  "late": 1,
  "excused": 0,
  "attendance_rate": 85.0
}
```

#### 5.5 `GET /groups`

**Query params:** `search`, `active_only`, `page`, `page_size`

```json
{
  "items": [
    {
      "id": 10,
      "name": "MT-21",
      "direction_id": 5,
      "direction_name": "Menejment",
      "course": 2,
      "leader_id": 100,
      "leader_name": "Sardorov S.",
      "student_count": 25,
      "is_active": true,
      "is_blocked": false,
      "created_at": "2025-09-01T00:00:00"
    }
  ],
  "total": 20,
  "page": 1,
  "page_size": 50
}
```

#### 5.6 `GET /students`

**Query params:** `search`, `group_id`, `page`, `page_size`

```json
{
  "items": [
    {
      "id": 1,
      "student_id": "12345678",
      "name": "Aliyev Ali",
      "user_id": 50,
      "group_id": 10,
      "group_name": "MT-21",
      "phone": "+998901234567",
      "email": "ali@mail.uz",
      "gender": "male",
      "contract_amount": 12000000.0,
      "contract_paid": 8000000.0,
      "is_active": true,
      "is_graduated": false,
      "avatar": null
    }
  ],
  "total": 500,
  "page": 1,
  "page_size": 20
}
```

#### 5.7 `GET /students/{id}`

```json
{
  "id": 1,
  "student_id": "12345678",
  "name": "Aliyev Ali",
  "user_id": 50,
  "group_id": 10,
  "group_name": "MT-21",
  "phone": "+998901234567",
  "email": "ali@mail.uz",
  "address": "Toshkent sh., Chilonzor t.",
  "commute": "metro",
  "passport": "AB1234567",
  "jshshir": "12345678901234",
  "birth_date": "2005-03-15",
  "gender": "male",
  "contract_amount": 12000000.0,
  "contract_paid": 8000000.0,
  "enrollment_date": "2024-09-01",
  "graduation_date": null,
  "is_active": true,
  "is_graduated": false,
  "avatar": null,
  "created_at": "2024-09-01T00:00:00"
}
```

#### 5.8 `GET /notifications`

**Query params:** `unread_only`, `page`, `page_size`

```json
{
  "items": [
    {
      "id": 1,
      "title": "Yangi xabar",
      "message": "Ertangi darslar bekor qilindi",
      "type": "info",
      "is_read": false,
      "sender_id": null,
      "created_at": "2026-02-18T10:00:00",
      "read_at": null
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

`type` qiymatlari: `"info"`, `"warning"`, `"error"`, `"success"`

---

### 6. Clubs — To'garaklar

**Prefix:** `/api/mobile/clubs`

| # | Metod | Endpoint | Auth | Tavsif |
|---|-------|----------|------|--------|
| 1 | `GET` | `/clubs` | ✅ | To'garaklar ro'yxati |
| 2 | `GET` | `/clubs/{id}` | ✅ | To'garak batafsil |
| 3 | `POST` | `/clubs/{id}/join` | ✅ | To'garakka qo'shilish |
| 4 | `DELETE` | `/clubs/{id}/leave` | ✅ | To'garakdan chiqish |

#### 6.1 `GET /clubs`

**Query params:**

| Param | Tur | Default | Tavsif |
|-------|-----|---------|--------|
| `category` | string? | - | Kategoriya filter |
| `search` | string? | - | Qidiruv |
| `active_only` | bool | true | Faqat faol |
| `page` | int | 1 | Sahifa |
| `page_size` | int | 50 | Hajm (1-100) |

```json
{
  "items": [
    {
      "id": 1,
      "name": "Dasturlash to'garagi",
      "description": "Python, Java, va boshqa tillar",
      "category": "IT",
      "image_url": "/uploads/club1.jpg",
      "leader_id": 5,
      "leader_name": "Usmonov D.",
      "member_count": 30,
      "max_members": 50,
      "schedule": "Har seshanba 15:00-17:00",
      "location": "305-xona",
      "is_active": true,
      "is_joined": false,
      "created_at": "2025-09-15T00:00:00"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 50
}
```

#### 6.2 `POST /clubs/{id}/join`

**Response (200):**
```json
{
  "message": "To'garakka muvaffaqiyatli qo'shildingiz"
}
```

**Xatolar:**
- `400` — Allaqachon a'zo / Joy qolmadi / To'garak faol emas
- `404` — To'garak topilmadi / Talaba profili topilmadi

---

### 7. Tournaments — Turnirlar

**Prefix:** `/api/mobile/tournaments`

| # | Metod | Endpoint | Auth | Tavsif |
|---|-------|----------|------|--------|
| 1 | `GET` | `/tournaments` | ✅ | Turnirlar ro'yxati |
| 2 | `GET` | `/tournaments/{id}` | ✅ | Turnir batafsil |
| 3 | `POST` | `/tournaments/{id}/register` | ✅ | Ro'yxatdan o'tish |
| 4 | `DELETE` | `/tournaments/{id}/unregister` | ✅ | Ro'yxatdan chiqish |

#### 7.1 `GET /tournaments`

**Query params:** `status`, `search`, `page`, `page_size`

```json
{
  "items": [
    {
      "id": 1,
      "name": "Matematika olimpiadasi",
      "description": "1-2 kurs talabalari uchun",
      "subject_id": 3,
      "subject_name": "Matematika",
      "start_date": "2026-03-01T09:00:00",
      "end_date": "2026-03-01T17:00:00",
      "registration_deadline": "2026-02-28T23:59:59",
      "participant_count": 45,
      "max_participants": 100,
      "prize": "1-o'rin: 500,000 so'm",
      "rules": "Har bir ishtirokchi 3 soatda 10 masala yechadi",
      "image_url": "/uploads/tournament1.jpg",
      "status": "registration",
      "is_registered": false,
      "is_active": true,
      "created_at": "2026-02-01T00:00:00"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 50
}
```

`status` qiymatlari: `"draft"`, `"registration"`, `"active"`, `"completed"`, `"cancelled"`

---

### 8. Reports — Hisobotlar

**Prefix:** `/api/mobile/reports`

| # | Metod | Endpoint | Auth | Rol | Tavsif |
|---|-------|----------|------|-----|--------|
| 1 | `GET` | `/reports` | ✅ | Leader/Admin | Hisobotlar ro'yxati |
| 2 | `POST` | `/reports` | ✅ | Leader | Hisobot yaratish |
| 3 | `GET` | `/reports/{id}` | ✅ | Leader/Admin | Hisobot batafsil |

#### 8.1 `GET /reports`

**Query params:** `status`, `group_id`, `page`, `page_size`

```json
{
  "items": [
    {
      "id": 1,
      "name": "Fevral oyi hisoboti",
      "description": "Oylik davomat hisoboti",
      "report_type": "attendance",
      "status": "pending",
      "group_id": 10,
      "group_name": "MT-21",
      "submitted_by": 100,
      "submitted_by_name": "Sardorov S.",
      "date": "2026-02-18",
      "content": "...",
      "approved_by": null,
      "approved_at": null,
      "rejection_reason": null,
      "created_at": "2026-02-18T10:00:00"
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

`report_type`: `"attendance"`, `"financial"`, `"academic"`, `"other"`  
`status`: `"pending"`, `"approved"`, `"rejected"`

#### 8.2 `POST /reports`

**Request:**
```json
{
  "name": "Fevral oyi hisoboti",
  "description": "Oylik davomat hisoboti",
  "report_type": "attendance",
  "group_id": 10,
  "date_from": "2026-02-01",
  "date_to": "2026-02-28"
}
```

---

### 9. Library — Kutubxona

**Prefix:** `/api/mobile/library`

| # | Metod | Endpoint | Auth | Tavsif |
|---|-------|----------|------|--------|
| 1 | `GET` | `/library/` | ✅ | Kitoblar ro'yxati |
| 2 | `GET` | `/library/categories` | ✅ | Kitob kategoriyalari |
| 3 | `GET` | `/library/my-borrows` | ✅ | Mening kitoblarim |
| 4 | `GET` | `/library/stats` | ✅ | Kutubxona statistikasi |
| 5 | `GET` | `/library/{id}` | ✅ | Kitob batafsil |
| 6 | `POST` | `/library/{id}/borrow` | ✅ | Kitob olish |

#### 9.1 `GET /library/`

**Query params:** `search`, `category`, `page`, `page_size`

```json
{
  "items": [
    {
      "id": 1,
      "title": "Oliy matematika",
      "author": "Piskunov N.S.",
      "category": "darslik",
      "language": "uz",
      "isbn": "978-9943-00-001-1",
      "total_copies": 10,
      "available_copies": 7,
      "cover_url": "/uploads/books/math.jpg",
      "description": "1-2 kurslar uchun darslik",
      "pages": 520,
      "year": 2022,
      "publisher": "O'qituvchi",
      "rating": 4.5,
      "view_count": 150,
      "status": "available"
    }
  ],
  "total": 200,
  "page": 1,
  "page_size": 20
}
```

#### 9.2 `GET /library/categories`

```json
[
  {"value": "darslik", "name": "Darslik"},
  {"value": "ilmiy", "name": "Ilmiy adabiyot"},
  {"value": "badiiy", "name": "Badiiy adabiyot"},
  {"value": "texnik", "name": "Texnik adabiyot"},
  {"value": "diniy", "name": "Diniy adabiyot"},
  {"value": "tarixiy", "name": "Tarixiy adabiyot"},
  {"value": "huquqiy", "name": "Huquqiy adabiyot"},
  {"value": "tibbiyot", "name": "Tibbiyot"},
  {"value": "iqtisodiyot", "name": "Iqtisodiyot"},
  {"value": "pedagogika", "name": "Pedagogika"},
  {"value": "psixologiya", "name": "Psixologiya"},
  {"value": "boshqa", "name": "Boshqa"}
]
```

#### 9.3 `GET /library/my-borrows`

```json
{
  "items": [
    {
      "id": 1,
      "book_id": 5,
      "book_title": "Oliy matematika",
      "book_author": "Piskunov N.S.",
      "book_cover": "/uploads/books/math.jpg",
      "borrow_date": "2026-02-10",
      "due_date": "2026-02-24",
      "return_date": null,
      "status": "active",
      "late_fee": 0
    }
  ],
  "total": 3,
  "page": 1,
  "page_size": 20
}
```

`status`: `"active"`, `"returned"`, `"overdue"`

#### 9.4 `GET /library/stats`

```json
{
  "total_books": 500,
  "available_books": 380,
  "my_total_borrows": 12,
  "my_active_borrows": 2
}
```

#### 9.5 `POST /library/{id}/borrow`

**Cheklovlar:** Maksimal 5 ta kitob bir vaqtda

```json
{
  "success": true,
  "message": "Kitob muvaffaqiyatli olindi",
  "due_date": "2026-03-04"
}
```

---

### 10. Canteen — Oshxona

**Prefix:** `/api/mobile/canteen`

| # | Metod | Endpoint | Auth | Tavsif |
|---|-------|----------|------|--------|
| 1 | `GET` | `/canteen/categories` | ✅ | Menu kategoriyalari |
| 2 | `GET` | `/canteen/menu` | ✅ | Menu ro'yxati |
| 3 | `POST` | `/canteen/orders` | ✅ | Buyurtma berish |
| 4 | `GET` | `/canteen/orders` | ✅ | Mening buyurtmalarim |

#### 10.1 `GET /canteen/categories`

```json
[
  {
    "id": 1,
    "name": "Birinchi taomlar",
    "description": "Sho'rvalar",
    "icon": "🍲",
    "color": "#FF6B35"
  }
]
```

#### 10.2 `GET /canteen/menu`

**Query params:** `category_id`, `search`, `available_only` (default: true)

```json
{
  "items": [
    {
      "id": 1,
      "name": "Osh",
      "description": "An'anaviy o'zbek oshi",
      "price": 25000.0,
      "image_url": "/uploads/menu/osh.jpg",
      "category_id": 2,
      "category_name": "Ikkinchi taomlar",
      "is_available": true,
      "is_vegetarian": false,
      "preparation_time": 15
    }
  ]
}
```

#### 10.3 `POST /canteen/orders`

**Request:**
```json
{
  "items": [
    {"menu_item_id": 1, "quantity": 2},
    {"menu_item_id": 5, "quantity": 1}
  ],
  "notes": "Achchiq bo'lmasin"
}
```

**Response (200):**
```json
{
  "success": true,
  "order_id": 42,
  "total": 75000.0,
  "status": "pending",
  "message": "Buyurtma qabul qilindi"
}
```

#### 10.4 `GET /canteen/orders`

**Query params:** `status`, `page`

```json
{
  "items": [
    {
      "id": 42,
      "order_number": "M-50-1708250000",
      "total": 75000.0,
      "status": "pending",
      "notes": "Achchiq bo'lmasin",
      "created_at": "2026-02-18T12:30:00",
      "items": [
        {"name": "Osh", "quantity": 2, "price": 25000, "total": 50000},
        {"name": "Salat", "quantity": 1, "price": 25000, "total": 25000}
      ],
      "item_count": 2
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

`status`: `"pending"`, `"preparing"`, `"ready"`, `"delivered"`, `"cancelled"`

---

### 11. Contracts — Kontraktlar

**Prefix:** `/api/mobile/contracts`

| # | Metod | Endpoint | Auth | Tavsif |
|---|-------|----------|------|--------|
| 1 | `GET` | `/contracts/my` | ✅ | Mening kontraktim |
| 2 | `GET` | `/contracts/group` | ✅ | Guruh kontraktlari (Leader) |

#### 11.1 `GET /contracts/my`

```json
{
  "has_contract": true,
  "student": {
    "id": 1,
    "name": "Aliyev Ali",
    "student_id": "12345678",
    "group_name": "MT-21"
  },
  "basic": {
    "contract_amount": 12000000.0,
    "contract_paid": 8000000.0,
    "contract_remaining": 4000000.0,
    "contract_percentage": 66.7
  },
  "contracts": [
    {
      "id": 1,
      "academic_year": "2025-2026",
      "course": 2,
      "direction": "Menejment",
      "education_form": "kunduzgi",
      "student_status": "o'qiyapti",
      "contract_amount": 12000000.0,
      "grant_percentage": 0.0,
      "grant_amount": 0.0,
      "total_paid": 8000000.0,
      "debt_amount": 4000000.0,
      "payment_percentage": 66.7,
      "refund_amount": 0.0
    }
  ]
}
```

#### 11.2 `GET /contracts/group`

```json
{
  "items": [
    {
      "student_id": 1,
      "name": "Aliyev Ali",
      "hemis_id": "12345678",
      "contract_amount": 12000000.0,
      "contract_paid": 12000000.0,
      "debt": 0.0,
      "percentage": 100.0,
      "is_paid": true
    }
  ],
  "total": 25,
  "group_name": "MT-21",
  "summary": {
    "total_students": 25,
    "total_contract": 300000000.0,
    "total_paid": 250000000.0,
    "total_debt": 50000000.0,
    "payment_rate": 83.3,
    "fully_paid": 15,
    "with_debt": 10
  }
}
```

---

### 12. Help/FAQ

**Prefix:** `/api/mobile/help`

| # | Metod | Endpoint | Auth | Tavsif |
|---|-------|----------|------|--------|
| 1 | `GET` | `/help/` | ✅ | FAQ ro'yxati |
| 2 | `GET` | `/help/{id}` | ✅ | FAQ batafsil |

#### 12.1 `GET /help/`

**Query params:** `category`, `search`

```json
{
  "items": [
    {
      "id": 1,
      "question": "Tizimga qanday kiraman?",
      "answer": "Sizga berilgan login va parol bilan...",
      "category": "auth"
    }
  ],
  "categories": [
    {"value": "auth", "name": "Kirish va parol"},
    {"value": "attendance", "name": "Davomat"},
    {"value": "schedule", "name": "Jadval"},
    {"value": "notifications", "name": "Bildirishnomalar"},
    {"value": "reports", "name": "Hisobotlar"},
    {"value": "students", "name": "Talabalar"},
    {"value": "technical", "name": "Texnik yordam"},
    {"value": "general", "name": "Umumiy"},
    {"value": "security", "name": "Xavfsizlik"}
  ]
}
```

---

### 13. Push Notifications

**Prefix:** `/api/mobile/push`

| # | Metod | Endpoint | Auth | Rol | Tavsif |
|---|-------|----------|------|-----|--------|
| 1 | `POST` | `/push/register` | ✅ | Hammasi | Device token ro'yxatdan o'tkazish |
| 2 | `DELETE` | `/push/unregister` | ✅ | Hammasi | Device token o'chirish |
| 3 | `POST` | `/push/send` | ✅ | Admin | Push xabar yuborish |
| 4 | `POST` | `/push/send-topic` | ✅ | Admin | Topikga yuborish |
| 5 | `POST` | `/push/subscribe` | ✅ | Hammasi | Topikga obuna bo'lish |
| 6 | `POST` | `/push/unsubscribe` | ✅ | Hammasi | Topikdan chiqish |
| 7 | `GET` | `/push/status` | ❌ | - | Servis holati |

#### 13.1 `POST /push/register`

**Request:**
```json
{
  "token": "firebase_device_token_here",
  "device_type": "android"
}
```

`device_type`: `"android"`, `"ios"`, `"web"`

#### 13.2 `POST /push/send` (Admin only)

**Request:**
```json
{
  "user_ids": [1, 2, 3],
  "title": "Muhim xabar",
  "body": "Ertangi darslar bekor qilindi",
  "data": {"type": "schedule_change"}
}
```

---

## 🖥 Web Panellar va API v1

Web API barcha funksiyalarni qamrab oladi. Mobile API'dan tashqari qo'shimcha endpointlar:

### Web API Prefixlari

**Base:** `/api/v1/*` (yoki `/api/*`)

| # | Prefix | Tag | Tavsif |
|---|--------|-----|--------|
| 1 | `/api/v1/auth` | Authentication | Web autentifikatsiya |
| 2 | `/api/v1/users` | Users | Foydalanuvchilar boshqaruvi |
| 3 | `/api/v1/students` | Students | Talabalar CRUD |
| 4 | `/api/v1/groups` | Groups | Guruhlar CRUD |
| 5 | `/api/v1/attendance` | Attendance | Davomat boshqaruvi |
| 6 | `/api/v1/schedule` | Schedule | Jadval CRUD |
| 7 | `/api/v1/notifications` | Notifications | Bildirishnomalar |
| 8 | `/api/v1/reports` | Reports | Hisobotlar |
| 9 | `/api/v1/excel` | Excel | Import/Export |
| 10 | `/api/v1/ai` | AI Analysis | AI tahlil (GPT) |
| 11 | `/api/v1/mutoola` | Mutoola | KUAF Mutoola integratsiya |
| 12 | `/api/v1/dashboard` | Dashboard | Web dashboard |
| 13 | `/api/v1/telegram/*` | Telegram Bot | Bot integratsiya |
| 14 | `/api/v1/files` | Files | Fayl yuklash/yuklab olish |
| 15 | `/api/v1/library` | Library | Kutubxona boshqaruvi |
| 16 | `/api/v1/canteen` | Canteen | Oshxona boshqaruvi |
| 17 | `/api/v1/clubs` | Clubs | To'garaklar CRUD |
| 18 | `/api/v1/subjects` | Subjects | Fanlar CRUD |
| 19 | `/api/v1/directions` | Directions | Yo'nalishlar CRUD |
| 20 | `/api/v1/tournaments` | Tournaments | Turnirlar boshqaruvi |
| 21 | `/api/v1/settings` | Settings | Tizim sozlamalari |
| 22 | `/api/v1/logs` | Logs | Faoliyat loglari (SuperAdmin) |
| 23 | `/api/v1/search` | Search | Global qidiruv |
| 24 | `/api/v1/statistics` | Statistics | Statistika |
| 25 | `/api/v1/faqs` | FAQs | FAQ boshqaruvi |
| 26 | `/api/v1/subscriptions` | Subscriptions | Obuna boshqaruvi |
| 27 | `/api/v1/market/*` | UniMarket | Marketplace |
| 28 | `/api/v1/landing` | Landing | Landing sahifa sozlamalari |
| 29 | `/api/v1/contracts` | Contracts | Kontrakt boshqaruvi |
| 30 | `/api/v1/quizzes` | Quizzes | Topshiriqlar/Flashcards |
| 31 | `/api/v1/holidays` | Holidays | Bayramlar/Dam olish kunlari |

### Web Panel Ekranlari (Rollar bo'yicha)

#### 🎓 Student Panel (`/student/*`)

| Sahifa | Route | Tavsif |
|--------|-------|--------|
| Dashboard | `/student/dashboard` | Asosiy panel |
| Jadval | `/student/schedule` | Dars jadvali |
| Davomat | `/student/attendance` | Davomat tarixi |
| Kutubxona | `/student/library` | Kitoblar |
| AI Tahlil | `/student/ai-analysis` | AI bilan tahlil |
| Bildirishnomalar | `/student/notifications` | Xabarlar |
| Profil | `/student/profile` | Shaxsiy ma'lumotlar |
| Sozlamalar | `/student/settings` | Sozlamalar |
| Yordam | `/student/help` | FAQ |
| To'garaklar | `/student/clubs` | To'garaklar |
| Oshxona | `/student/canteen` | Taomlar |
| Turnirlar | `/student/tournaments` | Turnirlar |
| Market | `/student/market` | UniMarket |
| Topshiriqlar | `/student/quizzes` | Quiz/Flashcard |
| Kredit modul | `/student/credit-module` | Kredit tizimi |

#### 👑 Leader Panel (`/leader/*`)

| Sahifa | Route | Tavsif |
|--------|-------|--------|
| Dashboard | `/leader/dashboard` | Guruh boshqaruvi |
| Davomat | `/leader/attendance` | Davomat belgilash |
| Talabalar | `/leader/students` | Guruh talabalari |
| Kontraktlar | `/leader/contracts` | Kontrakt ma'lumotlari |
| Jadval | `/leader/schedule` | Jadval |
| Hisobotlar | `/leader/reports` | Hisobot yuborish |
| Bildirishnomalar | `/leader/notifications` | Xabarlar |
| Analitika | `/leader/analytics` | Tahlillar |
| Fayllar | `/leader/files` | Fayl boshqaruvi |
| Obuna | `/leader/subscription` | Obuna holati |
| Market | `/leader/market` | UniMarket |
| Topshiriqlar | `/leader/quizzes` | Quiz/Flashcard |
| AI Tahlil | `/leader/ai-analysis` | AI tahlil |
| Kredit modul | `/leader/credit-module` | Kredit tizimi |
| Kutubxona | `/leader/library` | Kitoblar |
| To'garaklar | `/leader/clubs` | To'garaklar |
| Oshxona | `/leader/canteen` | Taomlar |
| Turnirlar | `/leader/tournaments` | Turnirlar |

#### ⚙️ Admin Panel (`/admin/*`)

| Sahifa | Route | Tavsif |
|--------|-------|--------|
| Dashboard | `/admin/dashboard` | Umumiy statistika |
| Davomat | `/admin/attendance` | Davomat boshqaruvi |
| Talabalar | `/admin/students` | Talabalar CRUD |
| Guruhlar | `/admin/groups` | Guruhlar CRUD |
| Foydalanuvchilar | `/admin/users` | User boshqaruvi |
| Kontraktlar | `/admin/contracts` | Kontraktlar |
| Hisobotlar | `/admin/reports` | Hisobotlar |
| Bildirishnomalar | `/admin/notifications` | Xabarlar |
| To'garaklar | `/admin/clubs` | To'garaklar CRUD |
| Oshxona | `/admin/canteen` | Oshxona boshqaruvi |
| Turnirlar | `/admin/tournaments` | Turnirlar CRUD |
| Fanlar | `/admin/subjects` | Fanlar CRUD |
| Bayramlar | `/admin/holidays` | Dam olish kunlari |
| Jadval | `/admin/schedule` | Jadval CRUD |
| Import | `/admin/import` | Excel import |
| AI Tahlil | `/admin/ai-analysis` | AI tahlil |
| Kredit modul | `/admin/credit-module` | Kredit tizimi |

#### 🛡 Super Admin Panel (`/super/*`)

| Sahifa | Route | Tavsif |
|--------|-------|--------|
| Dashboard | `/super/dashboard` | Tizim umumiy |
| Davomat | `/super/attendance` | Davomat (admin view) |
| Adminlar | `/super/admins` | Admin boshqaruvi |
| Sozlamalar | `/super/settings` | Tizim sozlamalari |
| Loglar | `/super/logs` | Faoliyat loglari |
| Landing | `/super/landing` | Landing sahifa |
| Talabalar | `/super/students` | Talabalar (admin view) |
| Guruhlar | `/super/groups` | Guruhlar (admin view) |
| Hisobotlar | `/super/reports` | Hisobotlar |
| Bildirishnomalar | `/super/notifications` | Xabarlar |
| Turnirlar | `/super/tournaments` | Turnirlar |
| Obunalar | `/super/subscriptions` | Obuna boshqaruvi |
| Telegram Bot | `/super/telegram-bot` | Bot sozlamalari |
| Bayramlar | `/super/holidays` | Dam olish kunlari |
| Jadval | `/super/schedule` | Jadval |
| Foydalanuvchilar | `/super/users` | Barcha userlar |
| Kontraktlar | `/super/contracts` | Barcha kontraktlar |
| Yordam boshqaruvi | `/super/help-manage` | FAQ CRUD |
| Import | `/super/import` | Excel import |
| Fanlar | `/super/subjects` | Fanlar |
| To'garaklar | `/super/clubs` | To'garaklar |
| Oshxona | `/super/canteen` | Oshxona |
| Market Admin | `/super/market` | UniMarket admin |
| AI Tahlil | `/super/ai-analysis` | AI tahlil |
| Kredit modul | `/super/credit-module` | Kredit tizimi |

---

## 📊 Data Modellar

### User

```
{
  id: int
  login: string          // Unikal login (talaba ID yoki username)
  email: string?         // Email
  name: string           // To'liq ism
  role: "student" | "leader" | "admin" | "superadmin"
  phone: string?
  avatar: string?        // Avatar URL
  is_active: bool
  group_id: int?         // Student/Leader uchun
  group_name: string?
}
```

### Student

```
{
  id: int
  student_id: string     // HEMIS ID (talaba raqami)
  name: string
  full_name: string
  user_id: int?          // User jadvalidagi ID
  group_id: int?
  group_name: string?
  phone: string?
  email: string?
  address: string?
  passport: string?
  jshshir: string?       // JSHSHIR raqami
  birth_date: date?
  gender: string?
  contract_amount: float
  contract_paid: float
  enrollment_date: date?
  graduation_date: date?
  is_active: bool
  is_graduated: bool
  avatar: string?
}
```

### Group

```
{
  id: int
  name: string           // "MT-21", "BH-11"
  code: string?
  direction_id: int?
  direction_name: string?
  course: int?
  leader_id: int?        // Sardor user ID
  leader_name: string?
  student_count: int
  is_active: bool
  is_blocked: bool
}
```

### Attendance

```
{
  id: int
  student_id: int
  date: date             // "2026-02-18"
  status: "present" | "absent" | "late" | "excused"
  notes: string?
  reason: string?
  marked_by: int?        // Kim belgilagan
}
```

### Schedule

```
{
  id: int
  subject: string        // Fan nomi
  start_time: string     // "09:00"
  end_time: string       // "10:20"
  room: string?          // Xona raqami
  teacher: string?       // O'qituvchi ismi
  day_of_week: string    // "MONDAY", "TUESDAY", ...
  is_cancelled: bool
  is_active: bool
}
```

### Notification

```
{
  id: int
  title: string
  message: string
  type: "info" | "warning" | "error" | "success"
  is_read: bool
  sender_id: int?
  created_at: datetime
  read_at: datetime?
}
```

### Club

```
{
  id: int
  name: string
  description: string?
  category: string?
  image_url: string?
  leader_name: string?
  member_count: int
  max_members: int
  schedule: string?
  location: string?
  is_active: bool
  is_joined: bool        // Joriy user a'zomi
}
```

### Tournament

```
{
  id: int
  name: string
  description: string?
  subject_name: string?
  start_date: datetime?
  end_date: datetime?
  registration_deadline: datetime?
  participant_count: int
  max_participants: int
  prize: string?
  rules: string?
  status: "draft" | "registration" | "active" | "completed" | "cancelled"
  is_registered: bool    // Joriy user ro'yxatdami
}
```

### Report

```
{
  id: int
  name: string
  description: string?
  report_type: "attendance" | "financial" | "academic" | "other"
  status: "pending" | "approved" | "rejected"
  group_id: int?
  group_name: string?
  date_from: date?
  date_to: date?
  created_by: int
  approved_by: int?
  rejection_reason: string?
}
```

### Book

```
{
  id: int
  title: string
  author: string
  category: string       // "darslik", "ilmiy", "badiiy", ...
  language: string       // "uz", "ru", "en"
  isbn: string?
  total_copies: int
  available_copies: int
  cover_url: string?
  description: string?
  pages: int?
  year: int?
  publisher: string?
  rating: float
  view_count: int
  status: string
}
```

### Contract

```
{
  id: int
  academic_year: string  // "2025-2026"
  course: int
  direction: string
  education_form: string
  student_status: string
  contract_amount: float
  grant_percentage: float
  grant_amount: float
  total_paid: float
  debt_amount: float
  payment_percentage: float
  refund_amount: float
}
```

### DashboardStats

```
{
  role: string
  total_students: int
  total_groups: int
  active_students: int
  active_groups: int
  today_present: int
  today_absent: int
  today_late: int
  today_excused: int
  today_attendance_rate: float
  week_attendance_rate: float
  month_attendance_rate: float
  unread_notifications: int
  today_lessons: int
  pending_reports: int
}
```

---

## ❌ Xatolar va Status Kodlar

### HTTP Status Kodlar

| Kod | Ma'nosi | Tavsif |
|-----|---------|--------|
| `200` | OK | Muvaffaqiyatli |
| `400` | Bad Request | Noto'g'ri so'rov |
| `401` | Unauthorized | Token eskirgan yoki noto'g'ri |
| `403` | Forbidden | Ruxsat yo'q |
| `404` | Not Found | Ma'lumot topilmadi |
| `422` | Unprocessable Entity | Validatsiya xatosi |
| `429` | Too Many Requests | Rate limit |
| `500` | Internal Server Error | Server xatosi |

### Xato Response Formati

```json
{
  "success": false,
  "error": "Xato tavsifi",
  "error_code": "API_ERROR"
}
```

### Token Yangilash Oqimi (401)

```
1. API so'rov → 401 Unauthorized
2. App avtomatik POST /auth/refresh chaqiradi
3. Yangi access_token olinadi
4. Asl so'rov qayta yuboriladi
5. Agar refresh ham 401 → Login sahifasiga
```

### Mobil Appdagi Xato Xabarlari (O'zbekcha)

| Holat | Xabar |
|-------|-------|
| Timeout | "Ulanish vaqti tugadi. Internetni tekshiring." |
| No connection | "Serverga ulanib bo'lmadi. Internet ulanishini tekshiring." |
| 400 | "Noto'g'ri so'rov" |
| 401 | "Login yoki parol noto'g'ri" |
| 403 | "Ruxsat yo'q" |
| 404 | "Ma'lumot topilmadi" |
| 422 | "Noto'g'ri ma'lumot formati" |
| 500 | "Server xatosi" |
| Unknown | "Noma'lum xatolik yuz berdi" |

---

## 🔧 Texnik Ma'lumotlar

### Server
- **Domain:** unicontrol.uz
- **Server:** VPS (vmi3078510)
- **OS:** Ubuntu Linux
- **Proxy:** Nginx
- **Containerization:** Docker Compose

### Backend Stack
- **Framework:** FastAPI
- **ORM:** SQLAlchemy (async)
- **DB:** PostgreSQL
- **Auth:** JWT (python-jose + bcrypt)
- **Server:** Uvicorn
- **Logging:** Loguru
- **Rate Limiting:** Redis-based middleware

### Mobile Stack
- **Framework:** Flutter (Dart)
- **State Management:** Riverpod
- **HTTP Client:** Dio
- **Routing:** GoRouter
- **Secure Storage:** flutter_secure_storage
- **Push:** Firebase Cloud Messaging

### Timeout Konfiguratsiya
- Connect timeout: 30 soniya
- Receive timeout: 30 soniya
- Send timeout: 30 soniya

---

> 📝 **Oxirgi yangilanish:** 2026-02-18  
> 🏷 **Versiya:** 2.0.0  
> 👨‍💻 **UniControl Team**
