"""
UniControl - AI Routes
======================
OpenAI integration endpoints for AI analysis.
Includes per-user monthly usage limits in UZS.

- Student: 1000 UZS/month
- Staff (leader/admin/super): 1500 UZS/month

Author: UniControl Team
Version: 2.0.0
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from loguru import logger

from app.database import get_db
from app.config import now_tashkent
from app.services.ai_service import AIService
from app.core.dependencies import get_current_active_user, require_leader
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.ai_usage import AIUsage
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.models.subscription import GroupSubscription, SubscriptionStatus
from app.models.group import Group

router = APIRouter()

# ================================================
# COST CONSTANTS & HELPERS
# ================================================
# GPT-4o-mini: ~$0.15/1M input, ~$0.60/1M output tokens
# Blended average: ~$0.30/1M tokens
# 1 USD ≈ 12,800 UZS → 1M tokens ≈ 3,840 UZS
COST_PER_TOKEN_UZS = 0.004  # ~0.004 UZS per token (conservative)

STUDENT_MONTHLY_LIMIT_UZS = 1000.0   # 1000 so'm / oy
STAFF_MONTHLY_LIMIT_UZS = 1500.0     # 1500 so'm / oy


def get_monthly_limit(role: UserRole) -> float:
    """Get monthly AI limit in UZS based on role."""
    if role == UserRole.STUDENT:
        return STUDENT_MONTHLY_LIMIT_UZS
    return STAFF_MONTHLY_LIMIT_UZS


async def get_or_create_usage(db: AsyncSession, user: User) -> AIUsage:
    """Get or create the current month's AI usage record for a user."""
    current_month = now_tashkent().strftime("%Y-%m")
    
    result = await db.execute(
        select(AIUsage).where(
            AIUsage.user_id == user.id,
            AIUsage.month == current_month
        )
    )
    usage = result.scalar_one_or_none()
    
    if not usage:
        usage = AIUsage(
            user_id=user.id,
            month=current_month,
            total_tokens=0,
            input_tokens=0,
            output_tokens=0,
            request_count=0,
            cost_uzs=0.0,
            limit_uzs=get_monthly_limit(user.role),
        )
        db.add(usage)
        await db.flush()
    
    return usage


async def check_ai_limit(db: AsyncSession, user: User) -> AIUsage:
    """Check if user has remaining AI budget. Raises 429 if exceeded."""
    usage = await get_or_create_usage(db, user)
    
    if usage.cost_uzs >= usage.limit_uzs:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "AI limit exceeded",
                "message": f"Oylik AI limiti tugadi ({int(usage.limit_uzs)} so'm). Keyingi oyda qayta tiklanadi.",
                "cost_uzs": round(usage.cost_uzs, 2),
                "limit_uzs": usage.limit_uzs,
                "remaining_uzs": 0,
                "request_count": usage.request_count,
                "month": usage.month,
            }
        )
    
    return usage


async def record_ai_usage(
    db: AsyncSession,
    usage: AIUsage,
    total_tokens: int,
    input_tokens: int = 0,
    output_tokens: int = 0
):
    """Record token usage and cost after an AI call."""
    cost = total_tokens * COST_PER_TOKEN_UZS
    
    usage.total_tokens += total_tokens
    usage.input_tokens += input_tokens
    usage.output_tokens += output_tokens
    usage.request_count += 1
    usage.cost_uzs += cost
    usage.updated_at = now_tashkent()
    
    await db.flush()
    return cost


# ================================================
# SUBSCRIPTION CHECK — AI faqat Pro/Unlimited uchun
# ================================================
# AI Tahlil faqat "pro" va "unlimited" obunalarda mavjud
AI_ALLOWED_PLANS = {"pro", "unlimited"}


async def check_ai_subscription(db: AsyncSession, user: User):
    """
    Check if user's group has AI access (pro or unlimited plan).
    Admin, superadmin, teacher, dean, academic_affairs, registrar always have access.
    Raises 403 if subscription doesn't include AI.
    """
    # Admin, superadmin va xodim rollari har doim ruxsat
    STAFF_ROLES = (
        UserRole.ADMIN, UserRole.SUPERADMIN,
        UserRole.TEACHER, UserRole.DEAN,
        UserRole.ACADEMIC_AFFAIRS, UserRole.REGISTRAR_OFFICE
    )
    if user.role in STAFF_ROLES:
        return True

    # Student yoki leader — guruh obunasini tekshirish
    student_result = await db.execute(
        select(Student).where(Student.user_id == user.id)
    )
    student = student_result.scalar_one_or_none()

    if not student or not student.group_id:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "no_group",
                "message": "Guruh topilmadi. AI tahlildan foydalanish uchun guruhga biriktirilgan bo'lishingiz kerak."
            }
        )

    # Guruh obunasini olish
    sub_result = await db.execute(
        select(GroupSubscription).where(
            GroupSubscription.group_id == student.group_id,
            GroupSubscription.status.in_([
                SubscriptionStatus.ACTIVE.value,
                SubscriptionStatus.TRIAL.value
            ])
        ).order_by(GroupSubscription.end_date.desc())
    )
    subscription = sub_result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "no_subscription",
                "message": "AI tahlildan foydalanish uchun obuna kerak. Pro yoki Unlimited rejaga o'ting.",
                "required_plans": list(AI_ALLOWED_PLANS)
            }
        )

    if subscription.plan_type not in AI_ALLOWED_PLANS:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "plan_not_supported",
                "message": f"AI tahlil faqat Pro va Unlimited obunalarda mavjud. Hozirgi rejangiz: {subscription.plan_type}.",
                "current_plan": subscription.plan_type,
                "required_plans": list(AI_ALLOWED_PLANS)
            }
        )

    return True


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


@router.get("/access")
async def check_ai_access(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    AI sahifasiga kirish huquqini tekshirish.
    Returns: { has_access: bool, current_plan: str|null, required_plans: [...] }
    """
    # Admin, superadmin va xodim rollari har doim ruxsat
    STAFF_ROLES = (
        UserRole.ADMIN, UserRole.SUPERADMIN,
        UserRole.TEACHER, UserRole.DEAN,
        UserRole.ACADEMIC_AFFAIRS, UserRole.REGISTRAR_OFFICE
    )
    if current_user.role in STAFF_ROLES:
        return {"has_access": True, "current_plan": "staff", "required_plans": list(AI_ALLOWED_PLANS)}

    # Student/Leader — guruh obunasini tekshirish
    student_result = await db.execute(
        select(Student).where(Student.user_id == current_user.id)
    )
    student = student_result.scalar_one_or_none()

    if not student or not student.group_id:
        return {"has_access": False, "current_plan": None, "required_plans": list(AI_ALLOWED_PLANS)}

    sub_result = await db.execute(
        select(GroupSubscription).where(
            GroupSubscription.group_id == student.group_id,
            GroupSubscription.status.in_([
                SubscriptionStatus.ACTIVE.value,
                SubscriptionStatus.TRIAL.value
            ])
        ).order_by(GroupSubscription.end_date.desc())
    )
    subscription = sub_result.scalar_one_or_none()

    if not subscription:
        return {"has_access": False, "current_plan": None, "required_plans": list(AI_ALLOWED_PLANS)}

    has_access = subscription.plan_type in AI_ALLOWED_PLANS
    return {
        "has_access": has_access,
        "current_plan": subscription.plan_type,
        "required_plans": list(AI_ALLOWED_PLANS)
    }


@router.get("/usage")
async def get_ai_usage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's AI usage for this month.
    """
    usage = await get_or_create_usage(db, current_user)
    
    remaining = max(0, usage.limit_uzs - usage.cost_uzs)
    # Estimate max requests: avg ~2.5 UZS per request
    avg_cost_per_request = (usage.cost_uzs / usage.request_count) if usage.request_count > 0 else 2.5
    max_requests = int(usage.limit_uzs / avg_cost_per_request) if avg_cost_per_request > 0 else 400
    remaining_requests = max(0, max_requests - usage.request_count)
    percentage = min(100, round((usage.request_count / max_requests) * 100, 1)) if max_requests > 0 else 0
    
    return {
        "month": usage.month,
        "cost_uzs": round(usage.cost_uzs, 2),
        "limit_uzs": usage.limit_uzs,
        "remaining_uzs": round(remaining, 2),
        "percentage_used": percentage,
        "total_tokens": usage.total_tokens,
        "request_count": usage.request_count,
        "max_requests": max_requests,
        "remaining_requests": remaining_requests,
        "is_limit_reached": usage.cost_uzs >= usage.limit_uzs,
    }


@router.post("/analyze/student", response_model=StudentAnalysisResponse)
async def analyze_student(
    request: StudentAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze a student's performance using AI.
    
    Students can only analyze themselves. Leaders and above can analyze any student.
    """
    # Obuna tekshirish — faqat Pro/Unlimited
    await check_ai_subscription(db, current_user)

    # Students can only analyze themselves
    if current_user.role == UserRole.STUDENT:
        student_result = await db.execute(
            select(Student).where(Student.user_id == current_user.id)
        )
        own_student = student_result.scalar_one_or_none()
        if not own_student or own_student.id != request.student_id:
            raise HTTPException(status_code=403, detail="Students can only analyze their own data")
    
    # Check AI limit
    usage = await check_ai_limit(db, current_user)
    
    service = AIService(db)
    result = await service.analyze_student(
        student_id=request.student_id,
        include_attendance=request.include_attendance,
        include_grades=request.include_grades,
        include_behavior=request.include_behavior
    )
    
    # Record usage
    tokens_used = result.get("tokens_used", 0) if isinstance(result, dict) else getattr(result, "tokens_used", 0)
    if tokens_used:
        await record_ai_usage(db, usage, tokens_used)
    
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
    # Obuna tekshirish — faqat Pro/Unlimited
    await check_ai_subscription(db, current_user)

    # Check AI limit
    usage = await check_ai_limit(db, current_user)
    
    service = AIService(db)
    result = await service.analyze_group(
        group_id=request.group_id,
        semester=request.semester,
        include_attendance=request.include_attendance,
        include_performance=request.include_performance
    )
    
    # Record usage
    tokens_used = result.get("tokens_used", 0) if isinstance(result, dict) else getattr(result, "tokens_used", 0)
    if tokens_used:
        await record_ai_usage(db, usage, tokens_used)
    
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
    current_user: User = Depends(get_current_active_user)
):
    """
    Predict attendance patterns using AI.
    
    Students can only predict their own attendance.
    """
    # Obuna tekshirish — faqat Pro/Unlimited
    await check_ai_subscription(db, current_user)

    # Students can only predict their own attendance
    if current_user.role == UserRole.STUDENT:
        if request.student_id:
            student_result = await db.execute(
                select(Student).where(Student.user_id == current_user.id)
            )
            own_student = student_result.scalar_one_or_none()
            if not own_student or own_student.id != request.student_id:
                raise HTTPException(status_code=403, detail="Students can only predict their own attendance")
        elif request.group_id:
            raise HTTPException(status_code=403, detail="Students cannot predict group attendance")
    
    # Check AI limit
    usage = await check_ai_limit(db, current_user)
    
    service = AIService(db)
    result = await service.predict_attendance(
        student_id=request.student_id,
        group_id=request.group_id,
        days_ahead=request.days_ahead
    )
    
    # Record usage
    tokens_used = result.get("tokens_used", 0) if isinstance(result, dict) else getattr(result, "tokens_used", 0)
    if tokens_used:
        await record_ai_usage(db, usage, tokens_used)
    
    return result


@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Chat with AI assistant.
    """
    # Obuna tekshirish — faqat Pro/Unlimited
    await check_ai_subscription(db, current_user)

    # Check AI limit
    usage = await check_ai_limit(db, current_user)
    
    service = AIService(db)
    result = await service.chat(
        message=request.message,
        context=request.context,
        conversation_history=request.conversation_history,
        user_role=current_user.role.value
    )
    
    # Record usage
    tokens_used = result.get("tokens_used", 0) if isinstance(result, dict) else getattr(result, "tokens_used", 0)
    if tokens_used:
        await record_ai_usage(db, usage, tokens_used)
    
    return result


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
    # Obuna tekshirish — faqat Pro/Unlimited
    await check_ai_subscription(db, current_user)

    # Check AI limit
    usage = await check_ai_limit(db, current_user)
    
    service = AIService(db)
    result = await service.summarize_report(
        report_id=request.report_id,
        language=request.language
    )
    
    # Record usage
    tokens_used = result.get("tokens_used", 0) if isinstance(result, dict) else getattr(result, "tokens_used", 0)
    if tokens_used:
        await record_ai_usage(db, usage, tokens_used)
    
    return result


@router.get("/insights/dashboard")
async def get_dashboard_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-generated insights for dashboard.
    
    All authenticated users can get insights for their role.
    """
    # Obuna tekshirish — faqat Pro/Unlimited
    await check_ai_subscription(db, current_user)

    # Check AI limit
    usage = await check_ai_limit(db, current_user)
    
    service = AIService(db)
    result = await service.get_dashboard_insights(current_user.id, current_user.role.value)
    
    # Record usage
    if isinstance(result, dict):
        tokens_used = result.get("tokens_used", 0)
        if tokens_used:
            await record_ai_usage(db, usage, tokens_used)
    
    return result


@router.get("/recommendations/{student_id}")
async def get_student_recommendations(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI recommendations for a student.
    
    Students can only get their own recommendations.
    """
    # Obuna tekshirish — faqat Pro/Unlimited
    await check_ai_subscription(db, current_user)

    # Students can only get their own recommendations
    if current_user.role == UserRole.STUDENT:
        student_result = await db.execute(
            select(Student).where(Student.user_id == current_user.id)
        )
        own_student = student_result.scalar_one_or_none()
        if not own_student or own_student.id != student_id:
            raise HTTPException(status_code=403, detail="Students can only view their own recommendations")
    
    # Check AI limit
    usage = await check_ai_limit(db, current_user)
    
    service = AIService(db)
    result = await service.get_recommendations(student_id)
    
    # Record usage
    if isinstance(result, dict):
        tokens_used = result.get("tokens_used", 0)
        if tokens_used:
            await record_ai_usage(db, usage, tokens_used)
    
    return result


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
    # Obuna tekshirish — faqat Pro/Unlimited
    await check_ai_subscription(db, current_user)

    # Check AI limit
    usage = await check_ai_limit(db, current_user)
    
    service = AIService(db)
    result = await service.generate_notification_text(request.context, request.tone)
    
    # Record usage
    if isinstance(result, dict):
        tokens_used = result.get("tokens_used", 0)
        if tokens_used:
            await record_ai_usage(db, usage, tokens_used)
    
    return result


@router.get("/health")
async def ai_health_check():
    """
    Check AI service health.
    """
    service = AIService(None)
    return await service.health_check()
