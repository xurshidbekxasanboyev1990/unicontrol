"""
Landing Page Settings Model
============================
Stores landing page content that can be managed by super admin.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from app.config import TASHKENT_TZ, now_tashkent
from app.database import Base


class LandingSettings(Base):
    """
    Landing page settings - singleton row (id=1).
    Stores all landing page editable content as JSON fields.
    """
    __tablename__ = "landing_settings"

    id = Column(Integer, primary_key=True, default=1)

    # Hero section stats
    hero_stats = Column(JSON, default=lambda: {
        "students_count": "500+",
        "groups_count": "50+",
        "result_percent": "99%"
    })

    # Social links
    social_links = Column(JSON, default=lambda: [
        {"name": "Telegram", "icon": "Send", "url": "https://t.me/unicontrol", "placeholder": "https://t.me/username"},
        {"name": "Instagram", "icon": "Globe", "url": "", "placeholder": "https://instagram.com/username"},
        {"name": "YouTube", "icon": "Globe", "url": "", "placeholder": "https://youtube.com/@channel"},
        {"name": "GitHub", "icon": "Github", "url": "https://github.com/unicontrol", "placeholder": "https://github.com/username"},
        {"name": "LinkedIn", "icon": "Linkedin", "url": "", "placeholder": "https://linkedin.com/company/name"},
        {"name": "Website", "icon": "Globe", "url": "", "placeholder": "https://example.com"}
    ])

    # Team members
    team_members = Column(JSON, default=lambda: [
        {
            "id": 1,
            "name": "Javlonbek To'ychiyev",
            "position": "Kafedra mudiri",
            "type": "pm",
            "social": {},
            "icon": "Crown",
            "gradient": "from-amber-500 to-orange-600"
        },
        {
            "id": 2,
            "name": "Obidjonov Behruzbek",
            "position": "UI/UX Dizayner",
            "type": "designer",
            "social": {},
            "icon": "Palette",
            "gradient": "from-violet-500 to-purple-600"
        },
        {
            "id": 3,
            "name": "Mannobov Xojisaid",
            "position": "Frontend Developer",
            "type": "frontend",
            "social": {},
            "icon": "Code",
            "gradient": "from-emerald-500 to-teal-600"
        },
        {
            "id": 4,
            "name": "Xasanboyev Xurshidbek",
            "position": "Backend Developer",
            "type": "backend",
            "social": {},
            "icon": "Server",
            "gradient": "from-cyan-500 to-blue-600"
        }
    ])

    # Contact info
    contact_info = Column(JSON, default=lambda: {
        "email": "info@unicontrol.uz",
        "phone": "+998 90 123 45 67",
        "telegram": "@unicontrol_uz",
        "address": "Toshkent sh., Chilonzor t."
    })

    # About section stats
    about_stats = Column(JSON, default=lambda: {
        "founded": "01.10.2025",
        "universities": "1",
        "users": "500+",
        "support": "24/7"
    })

    # Feature cards (for admin management)
    feature_cards = Column(JSON, default=lambda: [
        {"id": 1, "title": "Tezkor ishlash", "description": "Barcha ma'lumotlarga bir joydan kirishingiz mumkin", "icon": "Zap", "iconBg": "bg-amber-100", "iconColor": "text-amber-600", "section": "features", "active": True},
        {"id": 2, "title": "Dars jadvali", "description": "Real vaqtda yangilanuvchi interaktiv jadval", "icon": "Calendar", "iconBg": "bg-blue-100", "iconColor": "text-blue-600", "section": "features", "active": True},
        {"id": 3, "title": "AI Tahlil", "description": "Sun'iy intellekt yordamida o'qishingizni tahlil qiling", "icon": "Brain", "iconBg": "bg-violet-100", "iconColor": "text-violet-600", "section": "features", "active": True},
        {"id": 4, "title": "Ro'yxatdan o'ting", "description": "Tizimga kirish uchun birinchi qadam", "icon": "Users", "iconBg": "bg-emerald-100", "iconColor": "text-emerald-600", "section": "how-it-works", "active": True},
        {"id": 5, "title": "Ma'lumotlar xavfsiz", "description": "Barcha ma'lumotlar shifrlangan holda saqlanadi", "icon": "Shield", "iconBg": "bg-rose-100", "iconColor": "text-rose-600", "section": "faq", "active": True}
    ])

    # Trusted institutions
    trusted_by = Column(JSON, default=lambda: [
        {"name": "KUAF", "full_name": "Ko'p tarmoqli amaliy fanlar universiteti"}
    ])

    # Timestamps
    updated_at = Column(DateTime(timezone=True), default=now_tashkent, onupdate=now_tashkent)
