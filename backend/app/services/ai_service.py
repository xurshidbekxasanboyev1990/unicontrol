"""
UniControl - AI Service
=======================
Handles AI analysis using OpenAI API.

Author: UniControl Team
Version: 1.0.0
"""

import json
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
import openai

from app.config import settings, now_tashkent
from app.models.student import Student
from app.models.attendance import Attendance, AttendanceStatus
from app.models.report import Report, ReportType, ReportStatus
from app.schemas.report import AIAnalysisRequest, AIAnalysisResponse
from app.core.exceptions import BadRequestException, ExternalAPIException


class AIService:
    """AI analysis service using OpenAI."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def analyze(
        self,
        request: AIAnalysisRequest,
        user_id: int
    ) -> AIAnalysisResponse:
        """
        Perform AI analysis based on request.
        
        Args:
            request: Analysis request
            user_id: User performing the analysis
            
        Returns:
            AI analysis response
        """
        start_time = now_tashkent()
        
        # Gather context data
        context_data = await self._gather_context(request)
        
        # Build prompt
        system_prompt = self._build_system_prompt(request.context_type)
        user_prompt = self._build_user_prompt(request, context_data)
        
        # Call OpenAI API
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            result = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
        except openai.APIError as e:
            raise ExternalAPIException("OpenAI", str(e))
        
        # Parse recommendations if requested
        recommendations = None
        if request.include_recommendations:
            recommendations = self._extract_recommendations(result)
        
        # Save to database as report
        report = Report(
            name=f"AI Analysis - {request.context_type}",
            description=request.prompt[:200],
            report_type=ReportType.AI_ANALYSIS,
            status=ReportStatus.COMPLETED,
            created_by=user_id,
            date_from=request.date_from,
            date_to=request.date_to,
            group_id=request.group_id,
            ai_prompt=request.prompt,
            ai_result=result,
            ai_model=settings.OPENAI_MODEL,
            ai_tokens_used=tokens_used,
            started_at=start_time,
            completed_at=now_tashkent(),
        )
        
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        processing_time = (now_tashkent() - start_time).total_seconds()
        
        return AIAnalysisResponse(
            id=report.id,
            prompt=request.prompt,
            result=result,
            recommendations=recommendations,
            context_data=context_data,
            model_used=settings.OPENAI_MODEL,
            tokens_used=tokens_used,
            processing_time=processing_time,
            created_at=report.created_at,
        )
    
    async def _gather_context(self, request: AIAnalysisRequest) -> Dict[str, Any]:
        """Gather relevant data for context."""
        context = {}
        
        if request.context_type == "attendance":
            context = await self._get_attendance_context(
                request.group_id,
                request.student_id,
                request.date_from,
                request.date_to
            )
        elif request.context_type == "payment":
            context = await self._get_payment_context(
                request.group_id,
                request.student_id
            )
        elif request.context_type == "performance":
            context = await self._get_performance_context(
                request.group_id,
                request.student_id,
                request.date_from,
                request.date_to
            )
        
        return context
    
    async def _get_attendance_context(
        self,
        group_id: Optional[int],
        student_id: Optional[int],
        date_from: Optional[date],
        date_to: Optional[date]
    ) -> Dict[str, Any]:
        """Get attendance context data."""
        query = select(Attendance)
        
        if student_id:
            query = query.where(Attendance.student_id == student_id)
        elif group_id:
            query = query.join(Student).where(Student.group_id == group_id)
        
        if date_from:
            query = query.where(Attendance.date >= date_from)
        if date_to:
            query = query.where(Attendance.date <= date_to)
        
        result = await self.db.execute(query)
        attendances = result.scalars().all()
        
        total = len(attendances)
        present = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        absent = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
        late = sum(1 for a in attendances if a.status == AttendanceStatus.LATE)
        excused = sum(1 for a in attendances if a.status == AttendanceStatus.EXCUSED)
        
        return {
            "total_records": total,
            "present": present,
            "absent": absent,
            "late": late,
            "excused": excused,
            "attendance_rate": round(present / total * 100, 1) if total > 0 else 0,
            "absence_rate": round(absent / total * 100, 1) if total > 0 else 0,
            "late_rate": round(late / total * 100, 1) if total > 0 else 0,
            "period": f"{date_from or 'start'} - {date_to or 'now'}",
        }
    
    async def _get_payment_context(
        self,
        group_id: Optional[int],
        student_id: Optional[int]
    ) -> Dict[str, Any]:
        """Get payment context data."""
        query = select(Student).where(Student.is_active == True)
        
        if student_id:
            query = query.where(Student.id == student_id)
        elif group_id:
            query = query.where(Student.group_id == group_id)
        
        result = await self.db.execute(query)
        students = result.scalars().all()
        
        total_contract = sum(float(s.contract_amount) for s in students)
        total_paid = sum(float(s.contract_paid) for s in students)
        total_debt = total_contract - total_paid
        
        debtors = [s for s in students if not s.is_contract_paid]
        fully_paid = [s for s in students if s.is_contract_paid]
        
        return {
            "total_students": len(students),
            "total_contract": total_contract,
            "total_paid": total_paid,
            "total_debt": total_debt,
            "payment_rate": round(total_paid / total_contract * 100, 1) if total_contract > 0 else 0,
            "debtors_count": len(debtors),
            "fully_paid_count": len(fully_paid),
            "average_debt": round(total_debt / len(debtors), 0) if debtors else 0,
        }
    
    async def _get_performance_context(
        self,
        group_id: Optional[int],
        student_id: Optional[int],
        date_from: Optional[date],
        date_to: Optional[date]
    ) -> Dict[str, Any]:
        """Get combined performance context."""
        attendance = await self._get_attendance_context(group_id, student_id, date_from, date_to)
        payment = await self._get_payment_context(group_id, student_id)
        
        return {
            "attendance": attendance,
            "payment": payment,
        }
    
    def _build_system_prompt(self, context_type: str) -> str:
        """Build system prompt based on context type."""
        base_prompt = """Siz UniControl - universitetlar uchun boshqaruv tizimining 
AI tahlil yordamchisisiz. Sizning vazifangiz:
1. Berilgan ma'lumotlarni tahlil qilish
2. Aniq va foydali xulosalar chiqarish
3. Amaliy tavsiyalar berish
4. O'zbek tilida javob berish

"""
        
        context_prompts = {
            "attendance": """Siz davomat ma'lumotlarini tahlil qilasiz. 
E'tibor bering: 
- Umumiy davomat darajasi
- Kech qolish tendensiyalari
- Sababsiz qatnashmaslik
- Haftalik/oylik o'zgarishlar""",
            
            "payment": """Siz to'lov ma'lumotlarini tahlil qilasiz.
E'tibor bering:
- To'lov foizi
- Qarzdorlar soni va ulushi
- O'rtacha qarz miqdori
- To'lov tendensiyalari""",
            
            "performance": """Siz talabalarning umumiy ko'rsatkichlarini tahlil qilasiz.
E'tibor bering:
- Davomat va to'lov o'rtasidagi bog'liqlik
- Xavf ostidagi talabalar
- Guruh ko'rsatkichlari
- Yaxshilanish imkoniyatlari""",
            
            "general": """Siz umumiy ma'lumotlarni tahlil qilasiz."""
        }
        
        return base_prompt + context_prompts.get(context_type, context_prompts["general"])
    
    def _build_user_prompt(
        self,
        request: AIAnalysisRequest,
        context_data: Dict[str, Any]
    ) -> str:
        """Build user prompt with context."""
        prompt = f"""Foydalanuvchi so'rovi: {request.prompt}

Mavjud ma'lumotlar:
{json.dumps(context_data, indent=2, ensure_ascii=False)}

Iltimos, yuqoridagi ma'lumotlarni tahlil qiling va so'rovga javob bering.
"""
        
        if request.include_recommendations:
            prompt += "\n\nTavsiyalar bo'limini ham qo'shing."
        
        return prompt
    
    def _extract_recommendations(self, result: str) -> List[str]:
        """Extract recommendations from AI result."""
        recommendations = []
        
        # Try to find numbered recommendations
        lines = result.split("\n")
        in_recommendations = False
        
        for line in lines:
            line = line.strip()
            
            if any(word in line.lower() for word in ["tavsiya", "recommendation", "maslahat"]):
                in_recommendations = True
                continue
            
            if in_recommendations and line:
                # Check if it's a numbered item
                if line[0].isdigit() or line.startswith("-") or line.startswith("•"):
                    clean_line = line.lstrip("0123456789.-•) ").strip()
                    if clean_line:
                        recommendations.append(clean_line)
                elif not line[0].isalpha():
                    continue
                else:
                    # End of recommendations section
                    if len(recommendations) > 0:
                        break
        
        return recommendations[:10]  # Limit to 10 recommendations
    
    async def get_quick_insights(
        self,
        group_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get quick AI insights without full analysis."""
        # Gather basic stats
        attendance_context = await self._get_attendance_context(
            group_id, None, None, None
        )
        payment_context = await self._get_payment_context(group_id, None)
        
        insights = []
        
        # Attendance insights
        if attendance_context["attendance_rate"] < 80:
            insights.append({
                "type": "warning",
                "message": f"Davomat darajasi past: {attendance_context['attendance_rate']}%",
                "recommendation": "Talabalar bilan individual suhbatlar o'tkazing"
            })
        
        if attendance_context["late_rate"] > 10:
            insights.append({
                "type": "info",
                "message": f"Kech qolish darajasi: {attendance_context['late_rate']}%",
                "recommendation": "Dars vaqtlari haqida eslatma yuboring"
            })
        
        # Payment insights
        if payment_context["payment_rate"] < 70:
            insights.append({
                "type": "warning",
                "message": f"To'lov darajasi past: {payment_context['payment_rate']}%",
                "recommendation": "Qarzdorlarga to'lov eslatmalari yuboring"
            })
        
        if payment_context["debtors_count"] > 0:
            insights.append({
                "type": "info",
                "message": f"Qarzdorlar soni: {payment_context['debtors_count']}",
                "recommendation": f"O'rtacha qarz: {payment_context['average_debt']:,.0f} so'm"
            })
        
        return {
            "attendance": attendance_context,
            "payment": payment_context,
            "insights": insights,
            "generated_at": now_tashkent().isoformat(),
        }
