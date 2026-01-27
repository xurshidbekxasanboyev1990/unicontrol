"""
UniControl - Report Service
===========================
Handles report generation.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.report import Report, ReportType, ReportFormat, ReportStatus
from app.models.student import Student
from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.report import ReportCreate, ReportResponse
from app.core.exceptions import NotFoundException


class ReportService:
    """Report generation service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, report_id: int) -> Optional[Report]:
        """Get report by ID."""
        result = await self.db.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()
    
    async def list_reports(
        self,
        page: int = 1,
        page_size: int = 20,
        report_type: Optional[ReportType] = None,
        status: Optional[ReportStatus] = None,
        created_by: Optional[int] = None
    ) -> Tuple[List[Report], int]:
        """List reports with pagination."""
        query = select(Report)
        count_query = select(func.count(Report.id))
        
        if report_type:
            query = query.where(Report.report_type == report_type)
            count_query = count_query.where(Report.report_type == report_type)
        
        if status:
            query = query.where(Report.status == status)
            count_query = count_query.where(Report.status == status)
        
        if created_by:
            query = query.where(Report.created_by == created_by)
            count_query = count_query.where(Report.created_by == created_by)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        query = query.order_by(Report.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        reports = result.scalars().all()
        
        return list(reports), total
    
    async def create(
        self,
        report_data: ReportCreate,
        user_id: int
    ) -> Report:
        """Create a report."""
        report = Report(
            name=report_data.name,
            description=report_data.description,
            report_type=report_data.report_type,
            format=report_data.format,
            date_from=report_data.date_from,
            date_to=report_data.date_to,
            group_id=report_data.group_id,
            filters=report_data.filters,
            created_by=user_id,
            status=ReportStatus.PENDING,
        )
        
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        return report
    
    async def process_report(self, report_id: int) -> Report:
        """Process a pending report."""
        report = await self.get_by_id(report_id)
        if not report:
            raise NotFoundException("Report not found")
        
        report.status = ReportStatus.PROCESSING
        report.started_at = datetime.utcnow()
        await self.db.commit()
        
        try:
            # Generate report based on type
            if report.report_type == ReportType.ATTENDANCE:
                file_path = await self._generate_attendance_report(report)
            elif report.report_type == ReportType.PAYMENT:
                file_path = await self._generate_payment_report(report)
            elif report.report_type == ReportType.STUDENTS:
                file_path = await self._generate_students_report(report)
            else:
                file_path = await self._generate_generic_report(report)
            
            report.file_path = file_path
            report.status = ReportStatus.COMPLETED
            report.completed_at = datetime.utcnow()
            
        except Exception as e:
            report.status = ReportStatus.FAILED
            report.error_message = str(e)
            report.completed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(report)
        
        return report
    
    async def _generate_attendance_report(self, report: Report) -> str:
        """Generate attendance report data."""
        # This will be implemented with ExcelService
        return f"reports/attendance_{report.id}.xlsx"
    
    async def _generate_payment_report(self, report: Report) -> str:
        """Generate payment report data."""
        return f"reports/payment_{report.id}.xlsx"
    
    async def _generate_students_report(self, report: Report) -> str:
        """Generate students report data."""
        return f"reports/students_{report.id}.xlsx"
    
    async def _generate_generic_report(self, report: Report) -> str:
        """Generate generic report data."""
        return f"reports/report_{report.id}.xlsx"
    
    async def delete(self, report_id: int) -> bool:
        """Delete a report."""
        report = await self.get_by_id(report_id)
        if not report:
            raise NotFoundException("Report not found")
        
        await self.db.delete(report)
        await self.db.commit()
        
        return True
    
    async def get_dashboard_stats(
        self,
        group_id: Optional[int] = None
    ) -> dict:
        """Get dashboard statistics."""
        # Students stats
        student_query = select(func.count(Student.id)).where(Student.is_active == True)
        if group_id:
            student_query = student_query.where(Student.group_id == group_id)
        student_result = await self.db.execute(student_query)
        total_students = student_result.scalar()
        
        # Today's attendance
        today = date.today()
        attendance_query = select(Attendance).where(Attendance.date == today)
        if group_id:
            attendance_query = attendance_query.join(Student).where(
                Student.group_id == group_id
            )
        attendance_result = await self.db.execute(attendance_query)
        today_attendance = attendance_result.scalars().all()
        
        present = sum(1 for a in today_attendance if a.status == AttendanceStatus.PRESENT)
        absent = sum(1 for a in today_attendance if a.status == AttendanceStatus.ABSENT)
        late = sum(1 for a in today_attendance if a.status == AttendanceStatus.LATE)
        
        # Payment stats
        payment_result = await self.db.execute(
            select(
                func.sum(Student.contract_amount),
                func.sum(Student.contract_paid)
            ).where(Student.is_active == True)
        )
        payment_data = payment_result.one()
        total_contract = float(payment_data[0] or 0)
        total_paid = float(payment_data[1] or 0)
        
        return {
            "total_students": total_students,
            "today_attendance": {
                "present": present,
                "absent": absent,
                "late": late,
                "rate": float(present / (present + absent + late) * 100) if (present + absent + late) > 0 else 0
            },
            "payment": {
                "total_contract": total_contract,
                "total_paid": total_paid,
                "remaining": total_contract - total_paid,
                "percentage": float(total_paid / total_contract * 100) if total_contract > 0 else 0
            }
        }
