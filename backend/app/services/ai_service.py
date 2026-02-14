"""
UniControl - AI Service
=======================
Handles AI analysis using OpenAI API (GPT-4o-mini).
Full integration: student analysis, group analysis, chat, predictions, etc.

Author: UniControl Team
Version: 2.0.0
"""

import json
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import joinedload
import openai
from loguru import logger

from app.config import settings, now_tashkent, today_tashkent
from app.models.student import Student
from app.models.user import User
from app.models.group import Group
from app.models.attendance import Attendance, AttendanceStatus
from app.models.report import Report, ReportType, ReportStatus
from app.models.schedule import Schedule, WeekDay
from app.models.holiday import Holiday
from app.core.exceptions import BadRequestException, ExternalAPIException, NotFoundException


class AIService:
    """AI analysis service using OpenAI GPT-4o-mini."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        if settings.OPENAI_API_KEY:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
    
    def _check_api_key(self):
        """Ensure API key is configured."""
        if not self.client:
            raise BadRequestException("OpenAI API kaliti sozlanmagan. .env faylida OPENAI_API_KEY ni belgilang.")
    
    async def _call_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        response_format: str = None
    ) -> tuple:
        """Call OpenAI API and return (content, tokens_used)."""
        self._check_api_key()
        
        try:
            kwargs = {
                "model": settings.OPENAI_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            
            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}
            
            response = await self.client.chat.completions.create(**kwargs)
            
            content = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
            return content, tokens
            
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise ExternalAPIException("OpenAI", str(e))
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            raise ExternalAPIException("OpenAI", f"Kutilmagan xatolik: {str(e)}")

    # =========================================
    # STUDENT ANALYSIS
    # =========================================
    async def analyze_student(
        self,
        student_id: int,
        include_attendance: bool = True,
        include_grades: bool = True,
        include_behavior: bool = True
    ) -> Dict[str, Any]:
        """Analyze a student's performance using AI."""
        
        result = await self.db.execute(
            select(Student).options(joinedload(Student.group), joinedload(Student.user))
            .where(Student.id == student_id)
        )
        student = result.unique().scalar_one_or_none()
        if not student:
            raise NotFoundException(f"Talaba #{student_id} topilmadi")
        
        context = {}
        
        if include_attendance:
            date_from = today_tashkent() - timedelta(days=90)
            att_result = await self.db.execute(
                select(Attendance)
                .where(Attendance.student_id == student_id)
                .where(Attendance.date >= date_from)
                .order_by(Attendance.date.desc())
            )
            attendances = att_result.scalars().all()
            
            total = len(attendances)
            present = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
            absent = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
            late = sum(1 for a in attendances if a.status == AttendanceStatus.LATE)
            excused = sum(1 for a in attendances if a.status == AttendanceStatus.EXCUSED)
            
            context["attendance"] = {
                "total": total,
                "present": present,
                "absent": absent,
                "late": late,
                "excused": excused,
                "rate": round(present / total * 100, 1) if total > 0 else 0,
                "period_days": 90
            }
        
        student_name = student.user.name if student.user else f"Student #{student_id}"
        group_name = student.group.name if student.group else "N/A"
        
        context["student"] = {
            "name": student_name,
            "group": group_name,
            "is_active": student.is_active,
        }
        
        system_prompt = """Sen UniControl o'quv markazi boshqaruv tizimining AI tahlilchisisiz.
Talaba haqida berilgan ma'lumotlarni tahlil qilib, JSON formatda javob ber.

JSON format:
{
    "summary": "Talaba haqida umumiy xulosa (2-3 gap)",
    "strengths": ["Kuchli tomon 1", "Kuchli tomon 2"],
    "areas_for_improvement": ["Yaxshilash kerak 1", "Yaxshilash kerak 2"],
    "recommendations": ["Tavsiya 1", "Tavsiya 2", "Tavsiya 3"],
    "risk_level": "low|medium|high",
    "predicted_performance": "Bashorat matni"
}

O'zbek tilida javob ber. Aniq va foydali tavsiyalar ber."""

        user_prompt = f"""Talaba tahlili:

Talaba: {student_name}
Guruh: {group_name}

Ma'lumotlar:
{json.dumps(context, indent=2, ensure_ascii=False)}

Bu talabani tahlil qilib, JSON formatda natija ber."""

        content, tokens = await self._call_openai(
            system_prompt, user_prompt,
            max_tokens=1500, temperature=0.6,
            response_format="json"
        )
        
        try:
            result_data = json.loads(content)
        except json.JSONDecodeError:
            result_data = {
                "summary": content,
                "strengths": [],
                "areas_for_improvement": [],
                "recommendations": [],
                "risk_level": "medium",
                "predicted_performance": None
            }
        
        return {
            "student_id": student_id,
            "summary": result_data.get("summary", ""),
            "strengths": result_data.get("strengths", []),
            "areas_for_improvement": result_data.get("areas_for_improvement", []),
            "recommendations": result_data.get("recommendations", []),
            "risk_level": result_data.get("risk_level", "medium"),
            "predicted_performance": result_data.get("predicted_performance"),
            "tokens_used": tokens,
            "context_data": context
        }

    # =========================================
    # GROUP ANALYSIS
    # =========================================
    async def analyze_group(
        self,
        group_id: int,
        semester: Optional[int] = None,
        include_attendance: bool = True,
        include_performance: bool = True
    ) -> Dict[str, Any]:
        """Analyze a group's performance using AI."""
        
        group_result = await self.db.execute(
            select(Group).where(Group.id == group_id)
        )
        group = group_result.scalar_one_or_none()
        if not group:
            raise NotFoundException(f"Guruh #{group_id} topilmadi")
        
        students_result = await self.db.execute(
            select(Student).options(joinedload(Student.user))
            .where(Student.group_id == group_id)
        )
        students = students_result.unique().scalars().all()
        
        context = {
            "group": {"name": group.name, "total_students": len(students)},
        }
        
        if include_attendance:
            date_from = today_tashkent() - timedelta(days=30)
            top_performers = []
            at_risk = []
            total_rate = 0
            
            for s in students:
                att_result = await self.db.execute(
                    select(Attendance)
                    .where(Attendance.student_id == s.id)
                    .where(Attendance.date >= date_from)
                )
                atts = att_result.scalars().all()
                total = len(atts)
                present = sum(1 for a in atts if a.status == AttendanceStatus.PRESENT)
                rate = round(present / total * 100, 1) if total > 0 else 0
                total_rate += rate
                
                name = s.user.name if s.user else f"#{s.id}"
                student_info = {"name": name, "rate": rate}
                
                if rate >= 90:
                    top_performers.append(student_info)
                if rate < 70:
                    at_risk.append(student_info)
            
            avg_rate = round(total_rate / len(students), 1) if students else 0
            context["average_attendance"] = avg_rate
            context["top_performers"] = sorted(top_performers, key=lambda x: x["rate"], reverse=True)[:5]
            context["at_risk_students"] = sorted(at_risk, key=lambda x: x["rate"])[:5]
        
        system_prompt = """Sen UniControl o'quv markazi boshqaruv tizimining AI tahlilchisisiz.
Guruh haqida berilgan ma'lumotlarni tahlil qilib, JSON formatda javob ber.

JSON format:
{
    "summary": "Guruh haqida umumiy xulosa (2-3 gap)",
    "average_attendance": 85.5,
    "top_performers": [{"name": "Ism", "rate": 95.0}],
    "at_risk_students": [{"name": "Ism", "rate": 55.0}],
    "trends": ["Trend 1", "Trend 2"],
    "recommendations": ["Tavsiya 1", "Tavsiya 2"]
}

O'zbek tilida javob ber."""

        user_prompt = f"""Guruh tahlili:

Guruh: {group.name}
Talabalar soni: {len(students)}

Ma'lumotlar:
{json.dumps(context, indent=2, ensure_ascii=False)}

Bu guruhni tahlil qilib, JSON formatda natija ber."""

        content, tokens = await self._call_openai(
            system_prompt, user_prompt,
            max_tokens=1500, temperature=0.6,
            response_format="json"
        )
        
        try:
            result_data = json.loads(content)
        except json.JSONDecodeError:
            result_data = {
                "summary": content,
                "average_attendance": context.get("average_attendance", 0),
                "top_performers": context.get("top_performers", []),
                "at_risk_students": context.get("at_risk_students", []),
                "trends": [],
                "recommendations": []
            }
        
        return {
            "group_id": group_id,
            "summary": result_data.get("summary", ""),
            "average_attendance": result_data.get("average_attendance", 0),
            "top_performers": result_data.get("top_performers", []),
            "at_risk_students": result_data.get("at_risk_students", []),
            "trends": result_data.get("trends", []),
            "recommendations": result_data.get("recommendations", []),
            "tokens_used": tokens
        }

    # =========================================
    # ATTENDANCE PREDICTION
    # =========================================
    async def predict_attendance(
        self,
        student_id: Optional[int] = None,
        group_id: Optional[int] = None,
        days_ahead: int = 7
    ) -> Dict[str, Any]:
        """Predict attendance patterns using AI. Only for actual class days."""
        
        # ---- 1. Determine the relevant group_id ----
        resolved_group_id = group_id
        if student_id and not resolved_group_id:
            st_result = await self.db.execute(
                select(Student.group_id).where(Student.id == student_id)
            )
            resolved_group_id = st_result.scalar_one_or_none()
        
        # ---- 2. Get schedule days (which weekdays have classes) ----
        class_days_set = set()  # e.g. {"monday", "tuesday", ...}
        day_name_map = {
            "monday": "Dushanba",
            "tuesday": "Seshanba",
            "wednesday": "Chorshanba",
            "thursday": "Payshanba",
            "friday": "Juma",
            "saturday": "Shanba",
            "sunday": "Yakshanba",
        }
        
        if resolved_group_id:
            sched_result = await self.db.execute(
                select(Schedule.day_of_week)
                .where(Schedule.group_id == resolved_group_id)
                .where(Schedule.is_active == True)
                .distinct()
            )
            sched_days = sched_result.scalars().all()
            for d in sched_days:
                if d:
                    class_days_set.add(d.value if hasattr(d, 'value') else str(d).lower())
        
        # If no schedule found, default to Mon-Sat (no Sunday)
        if not class_days_set:
            class_days_set = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday"}
        
        # Remove Sunday explicitly (even if somehow in schedule)
        # class_days_set.discard("sunday")  # uncomment if Sunday should always be excluded
        
        # ---- 3. Build list of upcoming class days ----
        today = today_tashkent()
        
        # Load active holidays to exclude
        holiday_result = await self.db.execute(
            select(Holiday).where(
                Holiday.is_active == True,
                Holiday.end_date >= today,
            )
        )
        active_holidays = holiday_result.scalars().all()
        
        def is_holiday(check_d):
            """Check if a date falls within any active holiday"""
            for h in active_holidays:
                if h.start_date <= check_d <= h.end_date:
                    return True
            return False
        
        upcoming_class_days = []
        python_weekday_map = {
            0: "monday", 1: "tuesday", 2: "wednesday",
            3: "thursday", 4: "friday", 5: "saturday", 6: "sunday"
        }
        
        check_date = today + timedelta(days=1)
        while len(upcoming_class_days) < days_ahead:
            wd = python_weekday_map[check_date.weekday()]
            if wd in class_days_set and not is_holiday(check_date):
                upcoming_class_days.append({
                    "date": check_date.strftime("%Y-%m-%d"),
                    "weekday_en": wd,
                    "weekday_uz": day_name_map.get(wd, wd),
                })
            check_date += timedelta(days=1)
            # Safety: don't look more than 30 days ahead
            if (check_date - today).days > 30:
                break
        
        # ---- 4. Load historical attendance ----
        date_from = today - timedelta(days=60)
        query = select(Attendance).where(Attendance.date >= date_from)
        
        if student_id:
            query = query.where(Attendance.student_id == student_id)
        elif group_id:
            query = query.join(Student).where(Student.group_id == group_id)
        
        result = await self.db.execute(query.order_by(Attendance.date))
        attendances = result.scalars().all()
        
        total = len(attendances)
        present = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        absent = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
        late = sum(1 for a in attendances if a.status == AttendanceStatus.LATE)
        
        current_rate = round(present / total * 100, 1) if total > 0 else 0
        
        # Weekly rates only for class days
        weekly = {}
        for a in attendances:
            wd = python_weekday_map[a.date.weekday()]
            uz_day = day_name_map.get(wd, wd)
            if uz_day not in weekly:
                weekly[uz_day] = {"total": 0, "present": 0}
            weekly[uz_day]["total"] += 1
            if a.status == AttendanceStatus.PRESENT:
                weekly[uz_day]["present"] += 1
        
        weekly_rates = {}
        for day, data in weekly.items():
            weekly_rates[day] = round(data["present"] / data["total"] * 100, 1) if data["total"] > 0 else 0
        
        # Build the list of days to predict (in Uzbek)
        days_to_predict = [d["weekday_uz"] + f" ({d['date']})" for d in upcoming_class_days]
        class_days_uz = [day_name_map[d] for d in sorted(class_days_set) if d in day_name_map]
        
        system_prompt = """Sen davomat bashorat qiluvchi AI tizimisiz. Berilgan tarixiy ma'lumotlardan foydalanib bashorat qil.

MUHIM: Faqat dars bo'lgan kunlar uchun bashorat qil. Dam olish kunlari va dars bo'lmagan kunlarni QOSHMA.

JSON format:
{
    "predictions": [{"day": "Dushanba (2026-02-16)", "predicted_rate": 85, "reason": "Sabab"}],
    "confidence": 75,
    "factors": ["Omil 1", "Omil 2"],
    "overall_prediction": "Umumiy bashorat matni"
}

O'zbek tilida javob ber. predictions massivida FAQAT quyidagi kunlar bo'lsin."""

        user_prompt = f"""Davomat bashorati:

Hozirgi davomat: {current_rate}%
Tarixiy ma'lumotlar (60 kun): {total} yozuv
Kelgan: {present}, Kelmagan: {absent}, Kechikkan: {late}
Dars kunlari: {', '.join(class_days_uz)}
Hafta kunlari bo'yicha davomat: {json.dumps(weekly_rates, ensure_ascii=False)}

FAQAT quyidagi dars kunlari uchun bashorat qil (boshqa kun QO'SHMA):
{', '.join(days_to_predict)}

JSON formatda javob ber."""

        content, tokens = await self._call_openai(
            system_prompt, user_prompt,
            max_tokens=1000, temperature=0.5,
            response_format="json"
        )
        
        try:
            result_data = json.loads(content)
        except json.JSONDecodeError:
            result_data = {
                "predictions": [],
                "confidence": 50,
                "factors": ["Ma'lumot yetarli emas"],
                "overall_prediction": content
            }
        
        # Filter out any non-class days that AI might still include
        valid_uz_days = set(class_days_uz)
        filtered_predictions = []
        for pred in result_data.get("predictions", []):
            day_text = pred.get("day", "")
            # Check if prediction day matches a class day
            is_valid = any(uz_day in day_text for uz_day in valid_uz_days)
            if is_valid:
                filtered_predictions.append(pred)
        
        return {
            "predictions": filtered_predictions,
            "confidence": result_data.get("confidence", 50),
            "factors": result_data.get("factors", []),
            "overall_prediction": result_data.get("overall_prediction", ""),
            "class_days": class_days_uz,
            "tokens_used": tokens
        }

    # =========================================
    # AI CHAT
    # =========================================
    async def chat(
        self,
        message: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        user_role: str = "student"
    ) -> Dict[str, Any]:
        """Chat with AI assistant."""
        
        self._check_api_key()
        
        role_desc = {
            "student": "talaba",
            "leader": "guruh sardori",
            "admin": "administrator",
            "superadmin": "bosh administrator"
        }
        
        system_prompt = f"""Sen UniControl o'quv markazi boshqaruv tizimining AI yordamchisisiz.
Foydalanuvchi roli: {role_desc.get(user_role, user_role)}

Vazifalaring:
- O'quv markazi bilan bog'liq savollarga javob berish
- Davomat, o'qish, guruh boshqaruvi haqida maslahat berish
- Talabalar va o'qituvchilarga yordam berish
- O'zbek tilida samimiy va professional javob berish
- Qisqa va aniq javob berish (5-6 gap)

Agar savol o'quv markazi bilan bog'liq bo'lmasa, muloyimlik bilan buni ayt.
Har javob oxirida 2-3 ta tegishli qo'shimcha savol taklif qil."""

        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.append({"role": "user", "content": f"Kontekst: {context}"})
            messages.append({"role": "assistant", "content": "Tushundim, shu kontekstda yordam beraman."})
        
        if conversation_history:
            for msg in conversation_history[-6:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
            
            reply = response.choices[0].message.content
            tokens = response.usage.total_tokens
            
        except openai.APIError as e:
            raise ExternalAPIException("OpenAI", str(e))
        
        suggestions = []
        lines = reply.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("- ") or line.startswith("• ") or (len(line) > 3 and line[0].isdigit() and line[1] in '.):'):
                clean = line.lstrip("0123456789.-•) ").strip()
                if clean and "?" in clean:
                    suggestions.append(clean)
        
        return {
            "response": reply,
            "suggestions": suggestions[:5],
            "tokens_used": tokens
        }

    # =========================================
    # REPORT SUMMARY
    # =========================================
    async def summarize_report(
        self,
        report_id: int,
        language: str = "uz"
    ) -> Dict[str, Any]:
        """Summarize a report using AI."""
        
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        if not report:
            raise NotFoundException(f"Hisobot #{report_id} topilmadi")
        
        lang_map = {"uz": "O'zbek", "ru": "Rus", "en": "Ingliz"}
        lang_name = lang_map.get(language, "O'zbek")
        
        system_prompt = f"""Sen hisobotlarni xulosa qiluvchi AI yordamchisisiz.
{lang_name} tilida javob ber.

JSON format:
{{
    "summary": "Qisqa xulosa (2-3 gap)",
    "key_points": ["Asosiy nuqta 1", "Asosiy nuqta 2"],
    "action_items": ["Qilish kerak 1", "Qilish kerak 2"]
}}"""

        user_prompt = f"""Hisobot:
Nomi: {report.name}
Turi: {report.report_type.value if report.report_type else 'umumiy'}
Tavsif: {report.description or 'Tavsif yoq'}
Sana: {report.date_from} - {report.date_to}
Status: {report.status.value if report.status else 'nomalum'}

Xulosa qil. JSON formatda javob ber."""

        content, tokens = await self._call_openai(
            system_prompt, user_prompt,
            max_tokens=800, temperature=0.5,
            response_format="json"
        )
        
        try:
            result_data = json.loads(content)
        except json.JSONDecodeError:
            result_data = {"summary": content, "key_points": [], "action_items": []}
        
        return {
            "summary": result_data.get("summary", ""),
            "key_points": result_data.get("key_points", []),
            "action_items": result_data.get("action_items", []),
            "tokens_used": tokens
        }

    # =========================================
    # DASHBOARD INSIGHTS
    # =========================================
    async def get_dashboard_insights(
        self,
        user_id: int,
        user_role: str
    ) -> Dict[str, Any]:
        """Get AI-generated insights for dashboard."""
        
        today = today_tashkent()
        date_30 = today - timedelta(days=30)
        
        total_students_r = await self.db.execute(
            select(func.count(Student.id)).where(Student.is_active == True)
        )
        total_students = total_students_r.scalar() or 0
        
        att_result = await self.db.execute(
            select(Attendance).where(Attendance.date >= date_30)
        )
        attendances = att_result.scalars().all()
        total_att = len(attendances)
        present_att = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        overall_rate = round(present_att / total_att * 100, 1) if total_att > 0 else 0
        
        groups_r = await self.db.execute(select(func.count(Group.id)))
        total_groups = groups_r.scalar() or 0
        
        context = {
            "total_students": total_students,
            "total_groups": total_groups,
            "overall_attendance_rate": overall_rate,
            "total_attendance_records": total_att,
            "date_range": f"{date_30} - {today}",
            "user_role": user_role
        }
        
        system_prompt = """Sen UniControl dashboard uchun insight generatsiya qiluvchi AI siz.
Berilgan statistikadan foydali xulosalar chiqar.

JSON format:
{
    "insights": [
        {"type": "positive", "title": "Sarlavha", "description": "Tavsif", "action": null}
    ],
    "metrics": [
        {"label": "Metrika nomi", "value": "85%", "trend": 5, "type": "attendance"}
    ],
    "recommendations": [
        {"title": "Tavsiya", "description": "Batafsil", "priority": "high"}
    ],
    "summary": "Umumiy holat"
}

type qiymatlari: positive, warning, negative, info
priority: high, medium, low
O'zbek tilida, qisqa javob ber."""

        user_prompt = f"""Dashboard insight:

{json.dumps(context, indent=2, ensure_ascii=False)}

JSON formatda insight va tavsiyalar ber."""

        content, tokens = await self._call_openai(
            system_prompt, user_prompt,
            max_tokens=1500, temperature=0.6,
            response_format="json"
        )
        
        try:
            result_data = json.loads(content)
        except json.JSONDecodeError:
            result_data = {
                "insights": [{"type": "info", "title": "Tahlil", "description": content}],
                "metrics": [],
                "recommendations": [],
                "summary": content
            }
        
        result_data["tokens_used"] = tokens
        result_data["generated_at"] = now_tashkent().isoformat()
        return result_data

    # =========================================
    # STUDENT RECOMMENDATIONS
    # =========================================
    async def get_recommendations(self, student_id: int) -> Dict[str, Any]:
        """Get AI recommendations for a student."""
        
        result = await self.db.execute(
            select(Student).options(joinedload(Student.user), joinedload(Student.group))
            .where(Student.id == student_id)
        )
        student = result.unique().scalar_one_or_none()
        if not student:
            raise NotFoundException(f"Talaba #{student_id} topilmadi")
        
        date_from = today_tashkent() - timedelta(days=30)
        att_result = await self.db.execute(
            select(Attendance)
            .where(Attendance.student_id == student_id)
            .where(Attendance.date >= date_from)
        )
        attendances = att_result.scalars().all()
        total = len(attendances)
        present = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        absent = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
        rate = round(present / total * 100, 1) if total > 0 else 0
        
        student_name = student.user.name if student.user else f"#{student_id}"
        
        system_prompt = """Sen talabaga shaxsiy tavsiyalar beruvchi AI yordamchisiz.

JSON format:
{
    "recommendations": [
        {"title": "Tavsiya", "description": "Batafsil", "priority": "high", "category": "attendance"}
    ],
    "motivation": "Motivatsion matn",
    "goals": ["Maqsad 1", "Maqsad 2"]
}

category: attendance, study, social, health
O'zbek tilida, samimiy va motivatsion tarzda javob ber."""

        user_prompt = f"""Talaba: {student_name}
Guruh: {student.group.name if student.group else 'N/A'}
Oxirgi 30 kun davomati: {rate}% ({present}/{total} kelgan, {absent} kelmagan)

Shaxsiy tavsiyalar ber. JSON formatda."""

        content, tokens = await self._call_openai(
            system_prompt, user_prompt,
            max_tokens=1000, temperature=0.7,
            response_format="json"
        )
        
        try:
            result_data = json.loads(content)
        except json.JSONDecodeError:
            result_data = {
                "recommendations": [{"title": "Davomatni yaxshilang", "description": content, "priority": "medium", "category": "attendance"}],
                "motivation": "", "goals": []
            }
        
        result_data["student_id"] = student_id
        result_data["current_rate"] = rate
        result_data["tokens_used"] = tokens
        return result_data

    # =========================================
    # GENERATE NOTIFICATION TEXT
    # =========================================
    async def generate_notification_text(self, context: str, tone: str = "formal") -> Dict[str, Any]:
        """Generate notification text using AI."""
        
        tone_map = {"formal": "Rasmiy va professional", "friendly": "Samimiy va do'stona", "urgent": "Tezkor va jiddiy"}
        tone_desc = tone_map.get(tone, "Rasmiy")
        
        system_prompt = f"""Sen xabar matnlarini yozuvchi AI siz.
Stil: {tone_desc}
O'zbek tilida yoz. Qisqa va aniq bo'l.

JSON format:
{{
    "title": "Xabar sarlavhasi",
    "message": "Xabar matni",
    "variants": [{{"title": "Variant 2 sarlavha", "message": "Variant 2 matn"}}]
}}"""

        user_prompt = f"""Kontekst: {context}\n\n3 xil variant ber. JSON formatda."""

        content, tokens = await self._call_openai(
            system_prompt, user_prompt,
            max_tokens=800, temperature=0.8,
            response_format="json"
        )
        
        try:
            result_data = json.loads(content)
        except json.JSONDecodeError:
            result_data = {"title": "Bildirishnoma", "message": content, "variants": []}
        
        result_data["tokens_used"] = tokens
        return result_data

    # =========================================
    # QUICK INSIGHTS (no OpenAI - statistics only)
    # =========================================
    async def get_quick_insights(self, group_id: Optional[int] = None) -> Dict[str, Any]:
        """Get quick insights without OpenAI call."""
        
        date_from = today_tashkent() - timedelta(days=30)
        query = select(Attendance).where(Attendance.date >= date_from)
        if group_id:
            query = query.join(Student).where(Student.group_id == group_id)
        
        result = await self.db.execute(query)
        attendances = result.scalars().all()
        
        total = len(attendances)
        present = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        absent = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
        late = sum(1 for a in attendances if a.status == AttendanceStatus.LATE)
        rate = round(present / total * 100, 1) if total > 0 else 0
        late_rate = round(late / total * 100, 1) if total > 0 else 0
        
        insights = []
        if rate < 80:
            insights.append({"type": "warning", "title": "Past davomat", "message": f"Davomat: {rate}%", "recommendation": "Talabalar bilan suhbat o'tkazing"})
        elif rate >= 90:
            insights.append({"type": "positive", "title": "A'lo davomat", "message": f"Davomat: {rate}%", "recommendation": "Davom eting!"})
        
        if late_rate > 10:
            insights.append({"type": "info", "title": "Kechikishlar", "message": f"Kech qolish: {late_rate}%", "recommendation": "Eslatma yuboring"})
        
        return {
            "attendance": {"total": total, "present": present, "absent": absent, "late": late, "rate": rate, "late_rate": late_rate},
            "insights": insights,
            "generated_at": now_tashkent().isoformat(),
        }

    # =========================================
    # HEALTH CHECK
    # =========================================
    async def health_check(self) -> Dict[str, Any]:
        """Check AI service health."""
        status = {
            "service": "ai",
            "api_key_configured": bool(settings.OPENAI_API_KEY),
            "model": settings.OPENAI_MODEL,
            "status": "unknown"
        }
        
        if not settings.OPENAI_API_KEY:
            status["status"] = "no_api_key"
            status["message"] = "OpenAI API kaliti sozlanmagan"
            return status
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": "Salom, 1+1=?"}],
                max_tokens=10,
            )
            status["status"] = "healthy"
            status["message"] = "OpenAI API ishlayapti"
            status["test_tokens"] = response.usage.total_tokens
        except Exception as e:
            status["status"] = "error"
            status["message"] = str(e)
        
        return status
