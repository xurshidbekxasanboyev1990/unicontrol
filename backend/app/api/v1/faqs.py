"""
FAQ (Frequently Asked Questions) API Routes
============================================
Provides FAQs for the Help section.
Also provides contact-info and support-messages endpoints for HelpManageView.
"""

import datetime
from typing import List, Optional
from fastapi import APIRouter, Query, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.dependencies import get_current_active_user, require_admin
from app.models.user import User


router = APIRouter()


# ===== MODELS =====

class FAQItem(BaseModel):
    """FAQ item model"""
    id: int
    question: str
    answer: str
    category: str
    order: int = 0


class FAQResponse(BaseModel):
    """FAQ response model"""
    items: List[FAQItem]
    total: int


class FAQCreate(BaseModel):
    question: str
    answer: str
    category: str = "general"
    order: int = 0


class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    order: Optional[int] = None


class SupportMessageCreate(BaseModel):
    subject: str
    message: str
    category: str = "other"


# ===== IN-MEMORY STORAGE =====

# Default FAQs
DEFAULT_FAQS = [
    FAQItem(
        id=1,
        question="Tizimga qanday kiraman?",
        answer="Login va parolingizni kiritib 'Kirish' tugmasini bosing. Agar parolni unutgan bo'lsangiz, 'Parolni unutdim' havolasini bosing.",
        category="auth",
        order=1
    ),
    FAQItem(
        id=2,
        question="Parolni qanday o'zgartiraman?",
        answer="Profil -> Sozlamalar -> Parolni o'zgartirish bo'limiga o'ting va eski va yangi parolni kiriting.",
        category="auth",
        order=2
    ),
    FAQItem(
        id=3,
        question="Davomat qanday belgilanadi?",
        answer="Guruh rahbari yoki admin talabalar ro'yxatidan davomatni belgilaydi. Keldi, kelmadi yoki kechikdi statuslarini tanlash mumkin.",
        category="attendance",
        order=3
    ),
    FAQItem(
        id=4,
        question="Dars jadvalini qayerdan ko'raman?",
        answer="Asosiy menyudan 'Dars jadvali' bo'limiga o'ting. U yerda haftalik va oylik jadval ko'rsatiladi.",
        category="schedule",
        order=4
    ),
    FAQItem(
        id=5,
        question="Bildirishnomalar qayerda ko'rinadi?",
        answer="Bildirishnomalar ikonkasi yuqori o'ng burchakda joylashgan. Yangi bildirishnomalar qizil raqam bilan ko'rsatiladi.",
        category="notifications",
        order=5
    ),
    FAQItem(
        id=6,
        question="Hisobotlarni qanday yuklab olaman?",
        answer="Hisobotlar bo'limiga o'ting, kerakli hisobotni tanlang va 'Excel yuklash' yoki 'PDF yuklash' tugmasini bosing.",
        category="reports",
        order=6
    ),
    FAQItem(
        id=7,
        question="Guruhga talaba qanday qo'shiladi?",
        answer="Admin yoki guruh rahbari 'Talabalar' bo'limidan 'Yangi talaba' tugmasini bosib, ma'lumotlarni to'ldirishi kerak.",
        category="students",
        order=7
    ),
    FAQItem(
        id=8,
        question="Tizimda xatolik chiqsa nima qilaman?",
        answer="Sahifani yangilang (F5). Agar xatolik davom etsa, tizim administratoriga murojaat qiling.",
        category="technical",
        order=8
    ),
    FAQItem(
        id=9,
        question="Mobil ilovadan foydalanish mumkinmi?",
        answer="Ha, tizim mobil qurilmalarga moslashgan. Brauzer orqali telefon yoki planshetdan kirishingiz mumkin.",
        category="general",
        order=9
    ),
    FAQItem(
        id=10,
        question="Ma'lumotlarim xavfsizmi?",
        answer="Ha, barcha ma'lumotlar shifrlangan holda saqlanadi. Tizimga faqat login va parol bilan kirish mumkin.",
        category="security",
        order=10
    ),
]

# Custom FAQs (in-memory, resets on restart)
_custom_faqs: List[FAQItem] = []
_next_faq_id = 100

# Contact info (in-memory)
_contact_info = {
    "phones": ["+998 90 123 45 67"],
    "emails": ["info@unicontrol.uz"],
    "telegram": "@unicontrol_uz",
    "instagram": "",
    "facebook": "",
    "youtube": "",
    "address": "Toshkent shahri",
    "working_hours": "Dush-Juma 09:00-18:00"
}

# Support messages (in-memory)
_support_messages = []
_next_msg_id = 1


# ===== FAQ ENDPOINTS =====

@router.get("", response_model=FAQResponse)
async def get_faqs(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in questions/answers")
):
    """Get all FAQs with optional filtering."""
    faqs = DEFAULT_FAQS.copy() + _custom_faqs.copy()

    if category:
        faqs = [f for f in faqs if f.category == category]

    if search:
        search_lower = search.lower()
        faqs = [
            f for f in faqs
            if search_lower in f.question.lower() or search_lower in f.answer.lower()
        ]

    faqs.sort(key=lambda x: x.order)
    return FAQResponse(items=faqs, total=len(faqs))


@router.get("/categories")
async def get_faq_categories():
    """Get all FAQ categories."""
    return [
        {"id": "auth", "name": "Kirish va autentifikatsiya", "icon": "🔐"},
        {"id": "attendance", "name": "Davomat", "icon": "📋"},
        {"id": "schedule", "name": "Dars jadvali", "icon": "📅"},
        {"id": "notifications", "name": "Bildirishnomalar", "icon": "🔔"},
        {"id": "reports", "name": "Hisobotlar", "icon": "📊"},
        {"id": "students", "name": "Talabalar", "icon": "👨‍🎓"},
        {"id": "technical", "name": "Texnik yordam", "icon": "🔧"},
        {"id": "general", "name": "Umumiy", "icon": "ℹ️"},
        {"id": "security", "name": "Xavfsizlik", "icon": "🛡️"},
    ]


# ===== CONTACT INFO ENDPOINTS (before /{faq_id} to avoid path conflicts) =====

@router.get("/contact-info")
async def get_contact_info():
    """Get contact information for help section."""
    return _contact_info


@router.put("/contact-info")
async def update_contact_info(
    data: dict,
    current_user: User = Depends(require_admin)
):
    """Update contact information. Requires admin role."""
    global _contact_info
    allowed_keys = {"phones", "emails", "telegram", "instagram", "facebook", "youtube", "address", "working_hours"}
    for key, value in data.items():
        if key in allowed_keys:
            _contact_info[key] = value
    return {"message": "Aloqa ma'lumotlari yangilandi", "data": _contact_info}


# ===== SUPPORT MESSAGES ENDPOINTS (before /{faq_id}) =====

@router.get("/support-messages")
async def get_support_messages(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(require_admin)
):
    """Get all support messages. Requires admin role."""
    messages = _support_messages.copy()
    if status_filter:
        messages = [m for m in messages if m.get("status") == status_filter]
    return {"items": messages, "total": len(messages)}


@router.post("/support-messages", status_code=status.HTTP_201_CREATED)
async def create_support_message(
    data: SupportMessageCreate,
    current_user: User = Depends(get_current_active_user)
):
    """Create a support message."""
    global _next_msg_id
    msg = {
        "id": _next_msg_id,
        "user_id": current_user.id,
        "user_name": current_user.name,
        "subject": data.subject,
        "message": data.message,
        "category": data.category,
        "status": "open",
        "reply": None,
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
    _next_msg_id += 1
    _support_messages.append(msg)
    return msg


@router.post("/support-messages/{message_id}/reply")
async def reply_support_message(
    message_id: int,
    data: dict,
    current_user: User = Depends(require_admin)
):
    """Reply to a support message. Requires admin role."""
    for msg in _support_messages:
        if msg["id"] == message_id:
            msg["reply"] = data.get("reply", "")
            msg["status"] = "answered"
            return msg
    raise HTTPException(status_code=404, detail="Xabar topilmadi")


@router.patch("/support-messages/{message_id}/status")
async def update_support_message_status(
    message_id: int,
    data: dict,
    current_user: User = Depends(require_admin)
):
    """Update support message status. Requires admin role."""
    for msg in _support_messages:
        if msg["id"] == message_id:
            msg["status"] = data.get("status", msg["status"])
            return msg
    raise HTTPException(status_code=404, detail="Xabar topilmadi")


# ===== SINGLE FAQ GET (after static paths) =====

@router.get("/{faq_id}", response_model=FAQItem)
async def get_faq(faq_id: int):
    """Get a specific FAQ by ID."""
    all_faqs = DEFAULT_FAQS + _custom_faqs
    for faq in all_faqs:
        if faq.id == faq_id:
            return faq
    raise HTTPException(status_code=404, detail="FAQ topilmadi")


# ===== FAQ CRUD (Admin) =====

@router.post("", response_model=FAQItem, status_code=status.HTTP_201_CREATED)
async def create_faq(
    data: FAQCreate,
    current_user: User = Depends(require_admin)
):
    """Create a new FAQ. Requires admin role."""
    global _next_faq_id
    faq = FAQItem(
        id=_next_faq_id,
        question=data.question,
        answer=data.answer,
        category=data.category,
        order=data.order
    )
    _next_faq_id += 1
    _custom_faqs.append(faq)
    return faq


@router.put("/{faq_id}", response_model=FAQItem)
async def update_faq(
    faq_id: int,
    data: FAQUpdate,
    current_user: User = Depends(require_admin)
):
    """Update an existing FAQ. Requires admin role."""
    for i, faq in enumerate(_custom_faqs):
        if faq.id == faq_id:
            updated = faq.model_copy(update={k: v for k, v in data.model_dump().items() if v is not None})
            _custom_faqs[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="FAQ topilmadi")


@router.delete("/{faq_id}")
async def delete_faq(
    faq_id: int,
    current_user: User = Depends(require_admin)
):
    """Delete a FAQ. Requires admin role."""
    for i, faq in enumerate(_custom_faqs):
        if faq.id == faq_id:
            _custom_faqs.pop(i)
            return {"message": "FAQ o'chirildi"}
    raise HTTPException(status_code=404, detail="FAQ topilmadi")
