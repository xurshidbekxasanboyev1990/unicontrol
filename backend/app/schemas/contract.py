"""
UniControl - Contract Schemas
==============================
Pydantic schemas for contract-related operations.

Author: UniControl Team
Version: 1.0.0
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ContractBase(BaseModel):
    """Base contract schema."""
    student_id: int
    academic_year: str = Field(default="2025-2026", max_length=20)
    course: Optional[str] = Field(None, max_length=20)
    student_status: Optional[str] = Field(None, max_length=50)
    direction: Optional[str] = Field(None, max_length=200)
    education_form: Optional[str] = Field(None, max_length=50)
    contract_amount: Decimal = Field(default=0, ge=0)
    grant_percentage: Optional[float] = Field(None, ge=0, le=100)
    grant_amount: Decimal = Field(default=0, ge=0)
    debt_amount: Decimal = Field(default=0)
    payment_percentage: Optional[float] = None
    total_paid: Decimal = Field(default=0, ge=0)
    refund_amount: Decimal = Field(default=0, ge=0)
    year_start_balance: Decimal = Field(default=0)
    year_end_balance: Decimal = Field(default=0)
    note: Optional[str] = None


class ContractCreate(ContractBase):
    """Schema for creating a contract."""
    pass


class ContractUpdate(BaseModel):
    """Schema for updating a contract."""
    academic_year: Optional[str] = Field(None, max_length=20)
    course: Optional[str] = Field(None, max_length=20)
    student_status: Optional[str] = Field(None, max_length=50)
    direction: Optional[str] = Field(None, max_length=200)
    education_form: Optional[str] = Field(None, max_length=50)
    contract_amount: Optional[Decimal] = Field(None, ge=0)
    grant_percentage: Optional[float] = Field(None, ge=0, le=100)
    grant_amount: Optional[Decimal] = Field(None, ge=0)
    debt_amount: Optional[Decimal] = None
    payment_percentage: Optional[float] = None
    total_paid: Optional[Decimal] = Field(None, ge=0)
    refund_amount: Optional[Decimal] = Field(None, ge=0)
    year_start_balance: Optional[Decimal] = None
    year_end_balance: Optional[Decimal] = None
    note: Optional[str] = None


class ContractResponse(BaseModel):
    """Schema for contract response."""
    id: int
    student_id: int
    student_name: Optional[str] = None
    student_jshshir: Optional[str] = None
    group_name: Optional[str] = None
    academic_year: str
    course: Optional[str] = None
    student_status: Optional[str] = None
    direction: Optional[str] = None
    education_form: Optional[str] = None
    contract_amount: Decimal
    grant_percentage: Optional[float] = None
    grant_amount: Decimal
    debt_amount: Decimal
    payment_percentage: Optional[float] = None
    total_paid: Decimal
    refund_amount: Decimal
    year_start_balance: Decimal
    year_end_balance: Decimal
    remaining_amount: Decimal
    is_fully_paid: bool
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ContractListResponse(BaseModel):
    """Schema for paginated contract list."""
    items: List[ContractResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ContractStats(BaseModel):
    """Contract statistics."""
    total_contracts: int
    total_contract_amount: Decimal
    total_paid: Decimal
    total_debt: Decimal
    total_grant_amount: Decimal
    total_refund: Decimal
    payment_percentage: float
    fully_paid_count: int
    with_debt_count: int
    
    # By education form
    kunduzgi_count: int = 0
    sirtqi_count: int = 0
    
    # By status
    studying_count: int = 0
    academic_leave_count: int = 0
    other_status_count: int = 0


class ContractImportResult(BaseModel):
    """Result of contract import from Excel."""
    success: bool
    total_rows: int
    imported: int
    updated: int
    skipped: int
    failed: int
    errors: List[str] = []
    warnings: List[str] = []
