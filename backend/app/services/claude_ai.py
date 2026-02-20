"""
UniControl - Claude AI Service for Schedule Generation
======================================================
Uses Claude API to generate smart schedule suggestions.

Author: UniControl Team
Version: 1.0.0
"""

import httpx
import json
import logging
from typing import List, Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)


async def generate_schedule_with_ai(
    groups: List[Dict[str, Any]],
    subjects: List[Dict[str, Any]],
    teachers: List[Dict[str, Any]],
    rooms: List[str],
    constraints: Optional[str] = None,
    language: str = "uz"
) -> Dict[str, Any]:
    """
    Generate schedule using Claude AI.
    
    Args:
        groups: List of group dicts with id, name
        subjects: List of subject dicts with name, type, hours_per_week
        teachers: List of teacher dicts with id, name
        rooms: List of room names/numbers
        constraints: Additional constraints in natural language
        language: Response language (uz, ru, en)
    
    Returns:
        Generated schedule data
    """
    
    lang_map = {
        "uz": "o'zbek tilida",
        "ru": "на русском языке",
        "en": "in English"
    }
    lang_instruction = lang_map.get(language, "o'zbek tilida")
    
    groups_text = "\n".join([f"- {g['name']} (ID: {g['id']})" for g in groups])
    
    # Build subjects text with type and hours
    subjects_lines = []
    for s in subjects:
        if isinstance(s, dict):
            name = s.get('name', str(s))
            stype = s.get('type', 'lecture')
            hours = s.get('hours_per_week', 2)
            type_label = {'lecture': "ma'ruza", 'practice': 'amaliy', 'lab': 'laboratoriya', 'seminar': 'seminar'}.get(stype, stype)
            subjects_lines.append(f"- {name} ({type_label}, haftasiga {hours} soat)")
        else:
            subjects_lines.append(f"- {s}")
    subjects_text = "\n".join(subjects_lines)
    
    teachers_text = "\n".join([f"- {t['name']} (ID: {t['id']})" for t in teachers]) if teachers else "Ma'lumot yo'q"
    rooms_text = "\n".join([f"- {r}" for r in rooms]) if rooms else "Ma'lumot yo'q"
    
    prompt = f"""Sen universitetning akademik ishlar bo'limi uchun dars jadvali tuzuvchi AI yordamchisan.

Quyidagi ma'lumotlar asosida optimal dars jadvalini tuz:

GURUHLAR:
{groups_text}

FANLAR:
{subjects_text}

O'QITUVCHILAR:
{teachers_text}

XONALAR/AUDITORIYALAR:
{rooms_text}

DARS VAQTLARI (paralar):
1-para: 08:30-09:50
2-para: 10:00-11:20
3-para: 12:00-13:20
4-para: 13:30-14:50
5-para: 15:00-16:20

KUNLAR: monday, tuesday, wednesday, thursday, friday, saturday

{'QOSHIMCHA SHARTLAR: ' + constraints if constraints else ''}

MUHIM QOIDALAR:
1. Bir guruh bir vaqtda faqat bitta darsda bo'lishi mumkin
2. Bir o'qituvchi bir vaqtda faqat bitta guruhga dars bera oladi
3. Bir xonada bir vaqtda faqat bitta dars bo'lishi mumkin
4. Jadval optimal va muvozanatli bo'lsin
5. Har bir guruh uchun haftada kamida 1-2 ta bo'sh kun qoldiring
6. Dars turi: lecture (ma'ruza), practice (amaliy), lab (laboratoriya)

Javobni faqat JSON formatda ber, boshqa text yo'q. JSON structure:
{{
  "schedules": [
    {{
      "group_id": <int>,
      "group_name": "<string>",
      "subject": "<fan nomi>",
      "schedule_type": "lecture|practice|lab",
      "day_of_week": "monday|tuesday|...|saturday",
      "lesson_number": <1-5>,
      "start_time": "HH:MM",
      "end_time": "HH:MM",
      "room": "<xona>",
      "building": "<bino>",
      "teacher_name": "<o'qituvchi ismi>",
      "teacher_id": <int or null>,
      "color": "<#hex color>"
    }}
  ],
  "summary": "<jadval haqida qisqacha tushuntirish {lang_instruction}>"
}}

Ranglarni turli fanlar uchun turlicha ber (masalan: #E3F2FD - ko'k, #FFF3E0 - sariq, #E8F5E9 - yashil, #FCE4EC - pushti, #F3E5F5 - binafsha, #E0F7FA - zangori).
"""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                settings.CLAUDE_API_URL,
                headers={
                    "x-api-key": settings.CLAUDE_API_KEY or "",
                    "anthropic-version": settings.CLAUDE_ANTHROPIC_VERSION,
                    "content-type": "application/json"
                },
                json={
                    "model": settings.CLAUDE_MODEL,
                    "max_tokens": settings.CLAUDE_MAX_TOKENS,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return {
                    "error": True,
                    "message": f"Claude API xatosi: {response.status_code}",
                    "schedules": []
                }
            
            data = response.json()
            content = data.get("content", [{}])[0].get("text", "")
            
            # Parse JSON from response
            # Claude may wrap in ```json ... ```
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            result["error"] = False
            return result
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        return {
            "error": True,
            "message": "AI javobini o'qishda xatolik",
            "schedules": [],
            "raw_content": content if 'content' in dir() else ""
        }
    except httpx.TimeoutException:
        logger.error("Claude API timeout")
        return {
            "error": True,
            "message": "AI javob berish vaqti tugadi (timeout)",
            "schedules": []
        }
    except Exception as e:
        logger.error(f"Claude AI error: {e}")
        return {
            "error": True,
            "message": f"AI xatosi: {str(e)}",
            "schedules": []
        }


async def ai_optimize_schedule(
    current_schedules: List[Dict[str, Any]],
    problem_description: str,
    language: str = "uz"
) -> Dict[str, Any]:
    """
    Ask AI to optimize existing schedule based on a problem.
    """
    
    lang_map = {
        "uz": "o'zbek tilida",
        "ru": "на русском языке",
        "en": "in English"
    }
    lang_instruction = lang_map.get(language, "o'zbek tilida")
    
    schedules_text = json.dumps(current_schedules, ensure_ascii=False, indent=2)
    
    prompt = f"""Sen universitetning dars jadvalini optimallashtiruvchi AI yordamchisan.

HOZIRGI JADVAL:
{schedules_text}

MUAMMO/TALAB:
{problem_description}

Jadvalni optimallashtir va yangilangan versiyasini ber.
Javobni faqat JSON formatda ber:
{{
  "schedules": [...],
  "changes": [
    {{
      "description": "<o'zgarish tavsifi {lang_instruction}>",
      "old": {{...}},
      "new": {{...}}
    }}
  ],
  "summary": "<xulosa {lang_instruction}>"
}}
"""

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                settings.CLAUDE_API_URL,
                headers={
                    "x-api-key": settings.CLAUDE_API_KEY or "",
                    "anthropic-version": settings.CLAUDE_ANTHROPIC_VERSION,
                    "content-type": "application/json"
                },
                json={
                    "model": settings.CLAUDE_MODEL,
                    "max_tokens": settings.CLAUDE_MAX_TOKENS,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            )
            
            if response.status_code != 200:
                return {"error": True, "message": f"Claude API xatosi: {response.status_code}"}
            
            data = response.json()
            content = data.get("content", [{}])[0].get("text", "")
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            result["error"] = False
            return result
            
    except Exception as e:
        logger.error(f"AI optimize error: {e}")
        return {"error": True, "message": str(e)}
