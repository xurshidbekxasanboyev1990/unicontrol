"""
UniControl - AI Routes
======================
OpenAI integration endpoints for AI analysis.

Author: UniControl Team
Version: 1.0.0
"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from loguru import logger

from app.database import get_db
from app.services.ai_service import AIService
from app.core.dependencies import get_current_active_user, require_leader
from app.models.user import User
from app.models.student import Student
from app.models.notification import Notification, NotificationType, NotificationPriority

router = APIRouter()


# Request/Response Models
class StudentAnalysisRequest(BaseModel):
    """Request for student analysis."""
    student_id: int
    include_attendance: bool = True
    include_grades: bool = True
    include_behavior: bool = True


class StudentAnalysisResponse(BaseModel):
    """Response for student analysis."""
    student_id: int
    summary: str
    strengths: list[str]
    areas_for_improvement: list[str]
    recommendations: list[str]
    risk_level: str
    predicted_performance: Optional[str] = None


class GroupAnalysisRequest(BaseModel):
    """Request for group analysis."""
    group_id: int
    semester: Optional[int] = None
    include_attendance: bool = True
    include_performance: bool = True


class GroupAnalysisResponse(BaseModel):
    """Response for group analysis."""
    group_id: int
    summary: str
    average_attendance: float
    top_performers: list[dict]
    at_risk_students: list[dict]
    trends: list[str]
    recommendations: list[str]


class AttendancePredictionRequest(BaseModel):
    """Request for attendance prediction."""
    student_id: Optional[int] = None
    group_id: Optional[int] = None
    days_ahead: int = Field(default=7, ge=1, le=30)


class AttendancePredictionResponse(BaseModel):
    """Response for attendance prediction."""
    predictions: list[dict]
    confidence: float
    factors: list[str]


class ChatRequest(BaseModel):
    """Request for AI chat."""
    message: str
    context: Optional[str] = None
    conversation_history: Optional[list[dict]] = []


class ChatResponse(BaseModel):
    """Response for AI chat."""
    response: str
    suggestions: list[str] = []


class ReportSummaryRequest(BaseModel):
    """Request for report summary."""
    report_id: int
    language: str = "uz"


class ReportSummaryResponse(BaseModel):
    """Response for report summary."""
    summary: str
    key_points: list[str]
    action_items: list[str]


@router.post("/analyze/student", response_model=StudentAnalysisResponse)
async def analyze_student(
    request: StudentAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Analyze a student's performance using AI.
    
    Requires leader role or higher.
    """
    service = AIService(db)
    result = await service.analyze_student(
        student_id=request.student_id,
        include_attendance=request.include_attendance,
        include_grades=request.include_grades,
        include_behavior=request.include_behavior
    )
    
    # Send notification to student about AI analysis
    try:
        student_result = await db.execute(
            select(Student).where(Student.id == request.student_id)
        )
        student = student_result.scalar_one_or_none()
        if student and student.user_id:
            risk_text = ""
            if hasattr(result, 'risk_level') and result.risk_level:
                risk_map = {"low": "past", "medium": "o'rta", "high": "yuqori"}
                risk_text = f" Xavf darajasi: {risk_map.get(result.risk_level, result.risk_level)}."
            
            notification = Notification(
                user_id=student.user_id,
                title="AI tahlil natijalari tayyor 🤖",
                message=f"Sizning ko'rsatkichlaringiz AI tomonidan tahlil qilindi.{risk_text} Batafsil ma'lumot uchun AI tahlil sahifasini tekshiring.",
                type=NotificationType.INFO,
                priority=NotificationPriority.NORMAL,
                sender_id=current_user.id,
            )
            db.add(notification)
            await db.commit()
    except Exception as e:
        logger.warning(f"AI analysis notification error: {e}")
    
    return result


@router.post("/analyze/group", response_model=GroupAnalysisResponse)
async def analyze_group(
    request: GroupAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Analyze a group's performance using AI.
    
    Requires leader role or higher.
    """
    service = AIService(db)
    result = await service.analyze_group(
        group_id=request.group_id,
        semester=request.semester,
        include_attendance=request.include_attendance,
        include_performance=request.include_performance
    )
    
    # Send notification to all students in the group
    try:
        from app.models.group import Group
        group_result = await db.execute(
            select(Group).where(Group.id == request.group_id)
        )
        group = group_result.scalar_one_or_none()
        group_name = group.name if group else f"Guruh #{request.group_id}"
        
        students_result = await db.execute(
            select(Student.user_id)
            .where(Student.group_id == request.group_id)
            .where(Student.user_id.isnot(None))
        )
        user_ids = [row[0] for row in students_result.all()]
        
        for uid in user_ids:
            notification = Notification(
                user_id=uid,
                title="Guruh AI tahlili tayyor 📊",
                message=f"\"{group_name}\" guruhining ko'rsatkichlari AI tomonidan tahlil qilindi. Natijalarni AI tahlil sahifasida ko'ring.",
                type=NotificationType.INFO,
                priority=NotificationPriority.NORMAL,
                sender_id=current_user.id,
            )
            db.add(notification)
        await db.commit()
    except Exception as e:
        logger.warning(f"AI group analysis notification error: {e}")
    
    return result


@router.post("/predict/attendance", response_model=AttendancePredictionResponse)
async def predict_attendance(
    request: AttendancePredictionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Predict attendance patterns using AI.
    
    Requires leader role or higher.
    """
    service = AIService(db)
    return await service.predict_attendance(
        student_id=request.student_id,
        group_id=request.group_id,
        days_ahead=request.days_ahead
    )


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Chat with AI assistant.
    """
    service = AIService(db)
    return await service.chat(
        message=request.message,
        context=request.context,
        conversation_history=request.conversation_history,
        user_role=current_user.role.value
    )


@router.post("/summarize/report", response_model=ReportSummaryResponse)
async def summarize_report(
    request: ReportSummaryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Summarize a report using AI.
    
    Requires leader role or higher.
    """
    service = AIService(db)
    return await service.summarize_report(
        report_id=request.report_id,
        language=request.language
    )


@router.get("/insights/dashboard")
async def get_dashboard_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Get AI-generated insights for dashboard.
    
    Requires leader role or higher.
    """
    service = AIService(db)
    return await service.get_dashboard_insights(current_user.id, current_user.role.value)


@router.get("/recommendations/{student_id}")
async def get_student_recommendations(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Get AI recommendations for a student.
    
    Requires leader role or higher.
    """
    service = AIService(db)
    return await service.get_recommendations(student_id)


class NotificationTextRequest(BaseModel):
    """Request for notification text generation."""
    context: str
    tone: str = "formal"  # formal, friendly, urgent


@router.post("/generate/notification-text")
async def generate_notification_text(
    request: NotificationTextRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_leader)
):
    """
    Generate notification text using AI.
    
    Requires leader role or higher.
    """
    service = AIService(db)
    return await service.generate_notification_text(request.context, request.tone)


@router.get("/health")
async def ai_health_check():
    """
    Check AI service health.
    """
    service = AIService(None)
    return await service.health_check()
