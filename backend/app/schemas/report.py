"""
UniControl - Report Schemas
===========================
Pydantic schemas for report-related operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime, date
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.report import ReportType, ReportFormat, ReportStatus


class ReportBase(BaseModel):
    """Base report schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    report_type: ReportType
    format: ReportFormat = ReportFormat.EXCEL
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    group_id: Optional[int] = None
    filters: Optional[str] = None  # JSON string


class ReportCreate(ReportBase):
    """Schema for creating report."""
    pass


class ReportUpdate(BaseModel):
    """Schema for updating report."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ReportStatus] = None
    error_message: Optional[str] = None


class ReportGenerate(BaseModel):
    """Schema for generating report."""
    report_type: ReportType
    format: ReportFormat = ReportFormat.EXCEL
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    group_id: Optional[int] = None
    filters: Optional[dict] = None


class ReportResponse(BaseModel):
    """Schema for report response."""
    id: int
    name: str
    description: Optional[str] = None
    report_type: ReportType
    format: ReportFormat
    status: ReportStatus
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    group_id: Optional[int] = None
    group_name: Optional[str] = None
    filters: Optional[str] = None
    created_by: int
    created_by_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    download_url: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    ai_result: Optional[str] = None
    download_count: int
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    """Schema for report list."""
    items: List[ReportResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AIAnalysisRequest(BaseModel):
    """Schema for AI analysis request."""
    prompt: str = Field(..., min_length=10, max_length=2000)
    context_type: str = Field(
        default="attendance",
        pattern="^(attendance|payment|performance|general)$"
    )
    group_id: Optional[int] = None
    student_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    include_recommendations: bool = True


class AIAnalysisResponse(BaseModel):
    """Schema for AI analysis response."""
    id: int
    prompt: str
    result: str
    recommendations: Optional[List[str]] = None
    context_data: Optional[dict] = None
    model_used: str
    tokens_used: int
    processing_time: float
    created_at: datetime


class ExcelImportRequest(BaseModel):
    """Schema for Excel import request."""
    file_type: str = Field(..., pattern="^(students|attendance|schedule)$")
    group_id: Optional[int] = None
    update_existing: bool = True


class ExcelImportResponse(BaseModel):
    """Schema for Excel import response."""
    total_rows: int
    imported_count: int
    updated_count: int
    skipped_count: int
    failed_count: int
    errors: List[dict] = []


class ExcelExportRequest(BaseModel):
    """Schema for Excel export request."""
    export_type: str = Field(..., pattern="^(students|attendance|schedule|payments|report)$")
    group_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    include_all_columns: bool = False
