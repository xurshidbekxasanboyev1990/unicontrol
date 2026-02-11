"""
FAQ (Frequently Asked Questions) API Routes
============================================
Provides FAQs for the Help section.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel


router = APIRouter()


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


@router.get("", response_model=FAQResponse)
async def get_faqs(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in questions/answers")
):
    """
    Get all FAQs with optional filtering.
    
    Categories:
    - auth: Kirish va autentifikatsiya
    - attendance: Davomat
    - schedule: Dars jadvali
    - notifications: Bildirishnomalar
    - reports: Hisobotlar
    - students: Talabalar
    - technical: Texnik yordam
    - general: Umumiy
    - security: Xavfsizlik
    """
    faqs = DEFAULT_FAQS.copy()
    
    # Filter by category
    if category:
        faqs = [f for f in faqs if f.category == category]
    
    # Search
    if search:
        search_lower = search.lower()
        faqs = [
            f for f in faqs 
            if search_lower in f.question.lower() or search_lower in f.answer.lower()
        ]
    
    # Sort by order
    faqs.sort(key=lambda x: x.order)
    
    return FAQResponse(items=faqs, total=len(faqs))


@router.get("/categories")
async def get_faq_categories():
    """
    Get all FAQ categories.
    """
    categories = [
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
    return categories


@router.get("/{faq_id}", response_model=FAQItem)
async def get_faq(faq_id: int):
    """
    Get a specific FAQ by ID.
    """
    for faq in DEFAULT_FAQS:
        if faq.id == faq_id:
            return faq
    
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="FAQ topilmadi")
