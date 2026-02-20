"""
UniControl - Faculty Hierarchy Mapping
=======================================
Maps 20 directions (yo'nalishlar) to 3 super-faculties.

Author: UniControl Team
"""

# Mapping: direction (Group.faculty) → super-faculty
FACULTY_MAPPING = {
    # IT va Texnika fakulteti
    "Kompyuter injiniringi": "IT va Texnika",
    "Kompyuter injiniringi (Kompyuter injiniringi)": "IT va Texnika",
    "Iqtisodiyot": "IT va Texnika",
    "Iqtisodiyot (tarmoqlar va sohalar bo'yicha)": "IT va Texnika",
    "Moliya va moliyaviy texnologiyalar": "IT va Texnika",

    # Tibbiyot fakulteti
    "Davolash ishi": "Tibbiyot",
    "Pediatriya ishi": "Tibbiyot",
    "Stomatologiya": "Tibbiyot",
    "Farmatsiya": "Tibbiyot",
    "Farmatsiya (turlari bo'yicha)": "Tibbiyot",

    # Ijtimoiy-gumanitar fakulteti
    "Boshlang\u0027ich ta\u0027lim": "Ijtimoiy-gumanitar",
    "Boshlangʻich taʼlim": "Ijtimoiy-gumanitar",
    "Maktabgacha ta'lim": "Ijtimoiy-gumanitar",
    "Filologiya va tillarni o'qitish (ingliz tili)": "Ijtimoiy-gumanitar",
    "Filologiya va tillarni o'qitish (o'zbek tili)": "Ijtimoiy-gumanitar",
    "Filologiya va tillarni o'qitish (rus tili)": "Ijtimoiy-gumanitar",
    "Lingvistika (ingliz tili)": "Ijtimoiy-gumanitar",
    "Psixologiya": "Ijtimoiy-gumanitar",
    "Psixologiya (faoliyat turlari bo'yicha)": "Ijtimoiy-gumanitar",
    "Tarix": "Ijtimoiy-gumanitar",
    "Tarix (mamlakatlar va yo'nalishlar bo'yicha)": "Ijtimoiy-gumanitar",
}

FACULTY_ORDER = ["IT va Texnika", "Tibbiyot", "Ijtimoiy-gumanitar"]


def get_super_faculty(direction: str) -> str:
    """Get super-faculty for a direction. Falls back to 'Boshqa' if not found."""
    if not direction:
        return "Boshqa"
    # Exact match first
    if direction in FACULTY_MAPPING:
        return FACULTY_MAPPING[direction]
    # Try case-insensitive match
    for key, val in FACULTY_MAPPING.items():
        if key.lower() == direction.lower():
            return val
    # Try partial match
    direction_lower = direction.lower()
    if "kompyuter" in direction_lower or "iqtisod" in direction_lower or "moliya" in direction_lower:
        return "IT va Texnika"
    if "davolash" in direction_lower or "pediatr" in direction_lower or "stomat" in direction_lower or "farma" in direction_lower:
        return "Tibbiyot"
    return "Ijtimoiy-gumanitar"
