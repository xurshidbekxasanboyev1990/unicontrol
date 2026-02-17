"""
UniControl - Mobile Help Routes
================================
Mobile endpoints for FAQ/help.
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel

from app.models.user import User
from app.core.dependencies import get_current_active_user

router = APIRouter()


class FAQItem(BaseModel):
    id: int
    question: str
    answer: str
    category: str


FAQ_DATA = [
    FAQItem(id=1, question="Tizimga qanday kiraman?", answer="Sizga berilgan login va parol bilan tizimga kirishingiz mumkin. Login sifatida talaba ID raqamingiz ishlatiladi.", category="auth"),
    FAQItem(id=2, question="Parolni qanday o'zgartiraman?", answer="Profil > Sozlamalar > Parolni o'zgartirish bo'limiga o'ting. Joriy parolingizni va yangi parolni kiriting.", category="auth"),
    FAQItem(id=3, question="Parolimni unutdim, nima qilaman?", answer="O'quv bo'limi yoki administrator bilan bog'laning. Ular parolingizni tiklashga yordam beradi.", category="auth"),
    FAQItem(id=4, question="Davomat qanday belgilanadi?", answer="Guruh rahbari har bir dars uchun davomat belgilaydi. Siz o'z davomatingizni 'Davomat' bo'limida ko'rishingiz mumkin.", category="attendance"),
    FAQItem(id=5, question="Davomatim noto'g'ri belgilangan, nima qilaman?", answer="Guruh rahbaringizga murojaat qiling. Rahbar davomat ma'lumotlarini tuzatish huquqiga ega.", category="attendance"),
    FAQItem(id=6, question="Dars jadvali qayerda ko'rinadi?", answer="'Jadval' bo'limida haftalik dars jadvalingizni ko'rishingiz mumkin. Har bir kun uchun darslar vaqti, xonasi va o'qituvchisi ko'rsatiladi.", category="schedule"),
    FAQItem(id=7, question="Jadval o'zgarganda xabar keladimi?", answer="Ha, jadval o'zgarsa sizga bildirishnoma yuboriladi. Bildirishnomalar bo'limini tekshiring.", category="schedule"),
    FAQItem(id=8, question="Bildirishnomalar qanday ishlaydi?", answer="Tizim sizga muhim xabarlarni yuboradi: davomat, jadval o'zgarishlari, yangiliklar va boshqalar.", category="notifications"),
    FAQItem(id=9, question="Hisobot qanday yuboriladi?", answer="Guruh rahbari 'Hisobotlar' bo'limidan yangi hisobot yaratishi va yuborishi mumkin.", category="reports"),
    FAQItem(id=10, question="Kontrakt ma'lumotlarini qayerdan ko'raman?", answer="Profil bo'limida kontrakt summasi, to'langan va qoldiq summa ko'rsatiladi.", category="students"),
    FAQItem(id=11, question="Tizimda xatolik yuz bersa nima qilaman?", answer="Ilovani qayta ishga tushiring. Muammo davom etsa, administrator bilan bog'laning: admin@unicontrol.uz", category="technical"),
    FAQItem(id=12, question="Kutubxonadan kitob qanday olaman?", answer="'Kutubxona' bo'limida kitoblarni ko'rib, 'Olish' tugmasini bosing. Bir vaqtda 5 tagacha kitob olishingiz mumkin.", category="general"),
    FAQItem(id=13, question="To'garaklarga qanday yozilaman?", answer="'To'garaklar' bo'limida mavjud to'garaklarni ko'rib, 'Yozilish' tugmasini bosing.", category="general"),
    FAQItem(id=14, question="Turnirlarga qanday qatnashaman?", answer="'Turnirlar' bo'limida faol turnirlarni ko'ring va 'Ro'yxatdan o'tish' tugmasini bosing.", category="general"),
    FAQItem(id=15, question="Ma'lumotlarim xavfsizmi?", answer="Ha, barcha ma'lumotlar shifrlangan holda saqlanadi. Biz foydalanuvchilar maxfiyligini ta'minlaymiz.", category="security"),
]


@router.get("/")
async def get_faq_list(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
):
    """Get FAQ list with optional category filter and search."""
    items = FAQ_DATA

    if category:
        items = [f for f in items if f.category == category]

    if search:
        search_lower = search.lower()
        items = [f for f in items if search_lower in f.question.lower() or search_lower in f.answer.lower()]

    return {
        "items": [f.model_dump() for f in items],
        "categories": [
            {"value": "auth", "name": "Kirish va parol"},
            {"value": "attendance", "name": "Davomat"},
            {"value": "schedule", "name": "Jadval"},
            {"value": "notifications", "name": "Bildirishnomalar"},
            {"value": "reports", "name": "Hisobotlar"},
            {"value": "students", "name": "Talabalar"},
            {"value": "technical", "name": "Texnik yordam"},
            {"value": "general", "name": "Umumiy"},
            {"value": "security", "name": "Xavfsizlik"},
        ],
    }


@router.get("/{faq_id}")
async def get_faq_detail(
    faq_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Get single FAQ item."""
    for f in FAQ_DATA:
        if f.id == faq_id:
            return f.model_dump()
    raise HTTPException(status_code=404, detail="Savol topilmadi")
