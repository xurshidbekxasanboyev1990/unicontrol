"""
UniControl - API v1 Routes
==========================
Web API routes (including clubs, subjects, directions, tournaments, settings, logs).

Author: UniControl Team
Version: 1.0.2
Updated: 2026-01-29
"""

from fastapi import APIRouter

from app.api.v1 import (
    auth,
    users,
    students,
    groups,
    attendance,
    schedule,
    notifications,
    reports,
    excel,
    ai,
    mutoola,
    dashboard,
    telegram,
    files,
    library,
    canteen,
    clubs,
    subjects,
    directions,
    tournaments,
    system_settings,
    logs,
    statistics,
    faqs,
    subscriptions,
    market,
    sheets,
    landing,
    contracts,
    quizzes,
)

api_router = APIRouter()

# Authentication
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

# Users
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

# Students
api_router.include_router(
    students.router,
    prefix="/students",
    tags=["Students"]
)

# Groups
api_router.include_router(
    groups.router,
    prefix="/groups",
    tags=["Groups"]
)

# Attendance
api_router.include_router(
    attendance.router,
    prefix="/attendance",
    tags=["Attendance"]
)

# Schedule
api_router.include_router(
    schedule.router,
    prefix="/schedule",
    tags=["Schedule"]
)

# Notifications
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["Notifications"]
)

# Reports
api_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Reports"]
)

# Excel Import/Export
api_router.include_router(
    excel.router,
    prefix="/excel",
    tags=["Excel"]
)

# AI Analysis
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["AI Analysis"]
)

# Mutoola Integration
api_router.include_router(
    mutoola.router,
    prefix="/mutoola",
    tags=["Mutoola Integration"]
)

# Dashboard
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["Dashboard"]
)

# Telegram Bot Integration
api_router.include_router(
    telegram.router,
    tags=["Telegram Bot"]
)

# Files Management
api_router.include_router(
    files.router,
    prefix="/files",
    tags=["Files"]
)

# Library (Books)
api_router.include_router(
    library.router,
    prefix="/library",
    tags=["Library"]
)

# Canteen (Oshxona)
api_router.include_router(
    canteen.router,
    prefix="/canteen",
    tags=["Canteen"]
)

# Clubs (To'garaklar)
api_router.include_router(
    clubs.router,
    prefix="/clubs",
    tags=["Clubs"]
)

# Subjects (Fanlar)
api_router.include_router(
    subjects.router,
    prefix="/subjects",
    tags=["Subjects"]
)

# Directions (Yo'nalishlar)
api_router.include_router(
    directions.router,
    prefix="/directions",
    tags=["Directions"]
)

# Tournaments (Musobaqalar)
api_router.include_router(
    tournaments.router,
    prefix="/tournaments",
    tags=["Tournaments"]
)

# Settings (Sozlamalar)
api_router.include_router(
    system_settings.router,
    prefix="/settings",
    tags=["Settings"]
)

# Logs (Super Admin)
api_router.include_router(
    logs.router,
    prefix="/logs",
    tags=["Logs"]
)

# Statistics
api_router.include_router(
    statistics.router,
    prefix="/statistics",
    tags=["Statistics"]
)

# FAQs (Help)
api_router.include_router(
    faqs.router,
    prefix="/faqs",
    tags=["FAQs"]
)

# Subscriptions (Obuna)
api_router.include_router(
    subscriptions.router,
    prefix="/subscriptions",
    tags=["Subscriptions"]
)

# UniMarket (Marketplace)
api_router.include_router(
    market.router,
    tags=["UniMarket"]
)

# Google Sheets Schedule
api_router.include_router(
    sheets.router,
    prefix="/sheets",
    tags=["Google Sheets"]
)

# Landing Page Settings
api_router.include_router(
    landing.router,
    prefix="/landing",
    tags=["Landing"]
)

# Contracts (Kontrakt ma'lumotlari)
api_router.include_router(
    contracts.router,
    prefix="/contracts",
    tags=["Contracts"]
)

# Quizzes (Topshiriqlar/Flashcards)
api_router.include_router(
    quizzes.router,
    prefix="/quizzes",
    tags=["Quizzes"]
)
