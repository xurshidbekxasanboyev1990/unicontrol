"""
UniControl - Excel Service
==========================
Handles Excel import/export operations.

Author: UniControl Team
Version: 1.0.0
"""

import os
import io
from datetime import datetime, date
from app.config import now_tashkent
from decimal import Decimal
from typing import Optional, List, Tuple, Dict, Any
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models.student import Student
from app.models.group import Group
from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.report import ExcelImportResponse
from app.core.exceptions import BadRequestException


class ExcelService:
    """Excel import/export service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== EXPORT ====================
    
    async def export_students(
        self,
        group_id: Optional[int] = None,
        include_all_columns: bool = False
    ) -> io.BytesIO:
        """Export students to Excel."""
        query = select(Student).options(joinedload(Student.group))
        
        if group_id:
            query = query.where(Student.group_id == group_id)
        
        query = query.order_by(Student.name)
        
        result = await self.db.execute(query)
        students = result.unique().scalars().all()
        
        # Prepare data
        data = []
        for s in students:
            row = {
                "ID": s.student_id,
                "F.I.O": s.name,
                "Guruh": s.group.name if s.group else "",
                "Telefon": s.phone or "",
                "Email": s.email or "",
                "Tug'ilgan sana": s.birth_date.strftime("%d.%m.%Y") if s.birth_date else "",
                "Jinsi": "Erkak" if s.gender == "male" else "Ayol" if s.gender == "female" else "",
                "Kontrakt": float(s.contract_amount),
                "To'langan": float(s.contract_paid),
                "Qoldi": float(s.contract_remaining),
                "Holati": "Faol" if s.is_active else "Nofaol",
            }
            
            if include_all_columns:
                row.update({
                    "Manzil": s.address or "",
                    "Transport": s.commute or "",
                    "Pasport": s.passport or "",
                    "JSHSHIR": s.jshshir or "",
                    "Qabul sanasi": s.enrollment_date.strftime("%d.%m.%Y") if s.enrollment_date else "",
                    "Bitirish sanasi": s.graduation_date.strftime("%d.%m.%Y") if s.graduation_date else "",
                    "Guruh lideri": "Ha" if s.is_leader else "Yo'q",
                })
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        return self._create_excel_file(df, "Talabalar ro'yxati")
    
    async def export_attendance(
        self,
        group_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> io.BytesIO:
        """Export attendance to Excel."""
        query = select(Attendance).options(
            joinedload(Attendance.student).joinedload(Student.group)
        )
        
        if group_id:
            query = query.join(Student).where(Student.group_id == group_id)
        
        if date_from:
            query = query.where(Attendance.date >= date_from)
        if date_to:
            query = query.where(Attendance.date <= date_to)
        
        query = query.order_by(Attendance.date.desc(), Attendance.student_id)
        
        result = await self.db.execute(query)
        attendances = result.unique().scalars().all()
        
        # Prepare data
        status_map = {
            AttendanceStatus.PRESENT: "Keldi",
            AttendanceStatus.ABSENT: "Kelmadi",
            AttendanceStatus.LATE: "Kech qoldi",
            AttendanceStatus.EXCUSED: "Sababli",
        }
        
        data = []
        for a in attendances:
            data.append({
                "Sana": a.date.strftime("%d.%m.%Y"),
                "Talaba": a.student.name if a.student else "",
                "Guruh": a.student.group.name if a.student and a.student.group else "",
                "Holat": status_map.get(a.status, ""),
                "Kechikish (min)": a.late_minutes,
                "Fan": a.subject or "",
                "Para": a.lesson_number or "",
                "Izoh": a.note or "",
            })
        
        df = pd.DataFrame(data)
        
        return self._create_excel_file(df, "Davomat")
    
    async def export_payments(
        self,
        group_id: Optional[int] = None
    ) -> io.BytesIO:
        """Export payment report to Excel."""
        query = select(Student).options(joinedload(Student.group))
        
        if group_id:
            query = query.where(Student.group_id == group_id)
        
        query = query.where(Student.is_active == True)
        query = query.order_by(Student.name)
        
        result = await self.db.execute(query)
        students = result.unique().scalars().all()
        
        data = []
        for s in students:
            data.append({
                "ID": s.student_id,
                "F.I.O": s.name,
                "Guruh": s.group.name if s.group else "",
                "Kontrakt summasi": float(s.contract_amount),
                "To'langan": float(s.contract_paid),
                "Qolgan qarzi": float(s.contract_remaining),
                "To'lov %": f"{s.contract_percentage:.1f}%",
                "Holat": "To'liq to'langan" if s.is_contract_paid else "Qarzdor",
            })
        
        df = pd.DataFrame(data)
        
        return self._create_excel_file(df, "To'lovlar")
    
    def _create_excel_file(
        self,
        df: pd.DataFrame,
        title: str
    ) -> io.BytesIO:
        """Create styled Excel file from DataFrame."""
        output = io.BytesIO()
        
        wb = Workbook()
        ws = wb.active
        ws.title = title[:31]  # Max 31 chars for sheet name
        
        # Styles
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Add title
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(df.columns))
        ws.cell(1, 1, title)
        ws.cell(1, 1).font = Font(bold=True, size=14)
        ws.cell(1, 1).alignment = Alignment(horizontal="center")
        
        # Add date
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(df.columns))
        ws.cell(2, 1, f"Sana: {now_tashkent().strftime('%d.%m.%Y %H:%M')}")
        ws.cell(2, 1).alignment = Alignment(horizontal="right")
        
        # Write headers
        for col_idx, col_name in enumerate(df.columns, 1):
            cell = ws.cell(4, col_idx, col_name)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
        
        # Write data
        for row_idx, row in enumerate(df.values, 5):
            for col_idx, value in enumerate(row, 1):
                cell = ws.cell(row_idx, col_idx, value)
                cell.border = thin_border
                
                # Number formatting
                if isinstance(value, (int, float)):
                    cell.number_format = '#,##0'
        
        # Auto-adjust column widths
        for col_idx, col_name in enumerate(df.columns, 1):
            max_length = len(str(col_name))
            for row in df[col_name]:
                max_length = max(max_length, len(str(row)))
            ws.column_dimensions[chr(64 + col_idx)].width = min(max_length + 2, 50)
        
        wb.save(output)
        output.seek(0)
        
        return output
    
    # ==================== IMPORT ====================
    
    async def import_students(
        self,
        file: io.BytesIO,
        group_id: Optional[int] = None,
        update_existing: bool = True
    ) -> ExcelImportResponse:
        """Import students from Excel."""
        try:
            df = pd.read_excel(file, engine='openpyxl')
        except Exception as e:
            raise BadRequestException(f"Excel faylni o'qib bo'lmadi: {str(e)}")
        
        # Column mapping
        column_map = {
            "F.I.O": "name",
            "FIO": "name",
            "Ism": "name",
            "Telefon": "phone",
            "Tel": "phone",
            "Email": "email",
            "Pochta": "email",
            "Tug'ilgan sana": "birth_date",
            "Tug'ilgan": "birth_date",
            "Jinsi": "gender",
            "Jins": "gender",
            "Manzil": "address",
            "Pasport": "passport",
            "JSHSHIR": "jshshir",
            "PINFL": "jshshir",
            "Kontrakt": "contract_amount",
            "Shartnoma": "contract_amount",
            "To'langan": "contract_paid",
            "Guruh": "group_name",
        }
        
        # Rename columns
        df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
        
        total = len(df)
        imported = 0
        updated = 0
        skipped = 0
        failed = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                # Validate required fields
                name = str(row.get("name", "")).strip()
                if not name:
                    skipped += 1
                    continue
                
                # Parse data
                student_data = {
                    "name": name,
                    "phone": str(row.get("phone", "")).strip() or None,
                    "email": str(row.get("email", "")).strip() or None,
                    "passport": str(row.get("passport", "")).strip() or None,
                    "jshshir": str(row.get("jshshir", "")).strip() or None,
                    "address": str(row.get("address", "")).strip() or None,
                    "group_id": group_id,
                }
                
                # Parse birth_date
                birth_date = row.get("birth_date")
                if pd.notna(birth_date):
                    if isinstance(birth_date, str):
                        for fmt in ["%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"]:
                            try:
                                student_data["birth_date"] = datetime.strptime(birth_date, fmt).date()
                                break
                            except ValueError:
                                pass
                    elif isinstance(birth_date, datetime):
                        student_data["birth_date"] = birth_date.date()
                
                # Parse gender
                gender = str(row.get("gender", "")).strip().lower()
                if gender in ["erkak", "male", "m", "э"]:
                    student_data["gender"] = "male"
                elif gender in ["ayol", "female", "f", "а"]:
                    student_data["gender"] = "female"
                
                # Parse contract
                contract = row.get("contract_amount", 0)
                if pd.notna(contract):
                    student_data["contract_amount"] = Decimal(str(contract))
                
                paid = row.get("contract_paid", 0)
                if pd.notna(paid):
                    student_data["contract_paid"] = Decimal(str(paid))
                
                # Resolve group
                group_name = str(row.get("group_name", "")).strip()
                if group_name and not group_id:
                    group_result = await self.db.execute(
                        select(Group).where(Group.name == group_name)
                    )
                    group = group_result.scalar_one_or_none()
                    if group:
                        student_data["group_id"] = group.id
                
                # Check if student exists (by JSHSHIR or name+phone)
                existing = None
                if student_data.get("jshshir"):
                    result = await self.db.execute(
                        select(Student).where(Student.jshshir == student_data["jshshir"])
                    )
                    existing = result.scalar_one_or_none()
                
                if existing and update_existing:
                    # Update existing
                    for key, value in student_data.items():
                        if value is not None:
                            setattr(existing, key, value)
                    updated += 1
                elif not existing:
                    # Create new
                    # Generate student_id
                    year = now_tashkent().year
                    prefix = f"ST-{year}-"
                    max_result = await self.db.execute(
                        select(Student.student_id)
                        .where(Student.student_id.like(f"{prefix}%"))
                        .order_by(Student.student_id.desc())
                        .limit(1)
                    )
                    max_id = max_result.scalar()
                    if max_id:
                        num = int(max_id.split("-")[-1]) + 1
                    else:
                        num = 1
                    
                    student_data["student_id"] = f"{prefix}{num:04d}"
                    
                    student = Student(**student_data)
                    self.db.add(student)
                    imported += 1
                else:
                    skipped += 1
                
            except Exception as e:
                failed += 1
                errors.append({
                    "row": idx + 2,
                    "name": str(row.get("name", "")),
                    "error": str(e)
                })
        
        await self.db.commit()
        
        return ExcelImportResponse(
            total_rows=total,
            imported_count=imported,
            updated_count=updated,
            skipped_count=skipped,
            failed_count=failed,
            errors=errors
        )
    
    async def import_groups(
        self,
        file_data: bytes,
        update_existing: bool = False
    ) -> dict:
        """Import groups from Excel file."""
        try:
            df = pd.read_excel(io.BytesIO(file_data), engine='openpyxl')
        except Exception as e:
            raise BadRequestException(f"Excel faylni o'qib bo'lmadi: {str(e)}")
        
        # Column mapping
        column_map = {
            "Guruh kodi": "name",
            "Guruh nomi": "name",
            "Guruh": "name",
            "Kod": "name",
            "Name": "name",
            "Fakultet": "faculty",
            "Faculty": "faculty",
            "Yo'nalish": "faculty",
            "Kurs": "course_year",
            "Course": "course_year",
            "Bosqich": "course_year",
            "Kontrakt": "contract_amount",
            "Shartnoma summasi": "contract_amount",
            "Contract": "contract_amount",
        }
        
        # Rename columns
        df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
        
        total = len(df)
        imported = 0
        updated = 0
        skipped = 0
        failed = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                name = str(row.get("name", "")).strip()
                if not name:
                    skipped += 1
                    continue
                
                faculty = str(row.get("faculty", "")).strip() or "Noma'lum"
                
                # Parse course_year
                course_year = row.get("course_year", 1)
                if pd.isna(course_year):
                    course_year = 1
                else:
                    course_year = int(course_year)
                
                # Parse contract_amount
                contract_amount = row.get("contract_amount", 0)
                if pd.isna(contract_amount):
                    contract_amount = 0
                else:
                    contract_amount = Decimal(str(contract_amount))
                
                # Check existing
                result = await self.db.execute(
                    select(Group).where(Group.name == name)
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    if update_existing:
                        existing.faculty = faculty
                        existing.course_year = course_year
                        existing.contract_amount = contract_amount
                        updated += 1
                    else:
                        skipped += 1
                else:
                    group = Group(
                        name=name,
                        faculty=faculty,
                        course_year=course_year,
                        contract_amount=contract_amount,
                        is_active=True
                    )
                    self.db.add(group)
                    imported += 1
                    
            except Exception as e:
                failed += 1
                errors.append({
                    "row": idx + 2,
                    "name": str(row.get("name", "")),
                    "error": str(e)
                })
        
        await self.db.commit()
        
        return {
            "success": True,
            "total": total,
            "imported": imported,
            "updated": updated,
            "skipped": skipped,
            "failed": failed,
            "errors": errors
        }

    async def get_import_template(self, template_type: str) -> io.BytesIO:
        """Get import template Excel file."""
        if template_type == "students":
            columns = [
                "F.I.O", "Telefon", "Email", "Tug'ilgan sana", "Jinsi",
                "Manzil", "Pasport", "JSHSHIR", "Guruh", "Kontrakt", "To'langan"
            ]
            sample_data = [{
                "F.I.O": "Namuna Talaba",
                "Telefon": "+998901234567",
                "Email": "talaba@email.com",
                "Tug'ilgan sana": "01.01.2000",
                "Jinsi": "Erkak",
                "Manzil": "Toshkent sh.",
                "Pasport": "AA1234567",
                "JSHSHIR": "12345678901234",
                "Guruh": "101-guruh",
                "Kontrakt": 15000000,
                "To'langan": 5000000,
            }]
        elif template_type == "attendance":
            columns = ["Talaba ID", "Sana", "Holat", "Kechikish", "Fan", "Izoh"]
            sample_data = [{
                "Talaba ID": "ST-2024-0001",
                "Sana": now_tashkent().strftime("%d.%m.%Y"),
                "Holat": "Keldi",
                "Kechikish": 0,
                "Fan": "Matematika",
                "Izoh": "",
            }]
        else:
            raise BadRequestException(f"Unknown template type: {template_type}")
        
        df = pd.DataFrame(sample_data, columns=columns)
        
        return self._create_excel_file(df, f"{template_type}_template")

    async def import_kontingent(
        self,
        file_data: bytes,
        update_existing: bool = False,
        create_users: bool = True,
        default_password: str = "12345678"
    ) -> Dict[str, Any]:
        """
        Import students from Kontingent Excel file.
        OPTIMIZED: Batch insert for speed - can handle 20,000+ students in seconds.
        """
        from openpyxl import load_workbook
        from app.models.user import User, UserRole
        from app.core.security import get_password_hash
        import re
        
        # Load workbook with read_only for speed
        wb = load_workbook(io.BytesIO(file_data), read_only=True, data_only=True)
        ws = wb.active
        
        # Pre-hash the default password once (expensive operation)
        hashed_password = get_password_hash(default_password)
        
        # Load existing data in bulk for fast lookups
        existing_students_result = await self.db.execute(select(Student.student_id))
        existing_student_ids = set(row[0] for row in existing_students_result.fetchall())
        
        existing_users_result = await self.db.execute(select(User.login))
        existing_user_logins = set(row[0] for row in existing_users_result.fetchall())
        
        existing_groups_result = await self.db.execute(select(Group.id, Group.name))
        groups_cache = {row[1]: row[0] for row in existing_groups_result.fetchall()}
        
        # Collect all data first (in memory)
        students_to_create = []
        users_to_create = []
        groups_to_create = {}  # name -> group_data
        student_user_links = []  # [(student_id, user_login), ...]
        
        imported = 0
        updated = 0
        skipped = 0
        failed = 0
        errors = []
        users_created = 0
        
        # Read all rows at once
        rows = list(ws.iter_rows(min_row=3, values_only=True))
        
        for row_idx, row in enumerate(rows, start=3):
            try:
                if not row or len(row) < 2:
                    continue
                    
                # Read cell values (by index, 0-based)
                student_id = str(row[0] or "").strip()
                full_name = str(row[1] or "").strip()
                
                # Skip empty rows
                if not student_id or not full_name:
                    continue
                
                # Check if already exists
                if student_id in existing_student_ids:
                    skipped += 1
                    continue
                
                # Parse all fields
                passport = str(row[3] or "").strip() if len(row) > 3 else ""
                jshshir = str(row[4] or "").strip() if len(row) > 4 else ""
                birth_date = row[6] if len(row) > 6 else None
                phone = str(row[7] or "").strip() if len(row) > 7 else ""
                specialty_name = str(row[12] or "").strip() if len(row) > 12 else ""
                course = row[13] if len(row) > 13 else None
                group_name = str(row[14] or "").strip() if len(row) > 14 else ""
                
                # Address columns
                country = str(row[15] or "").strip() if len(row) > 15 else ""
                region = str(row[16] or "").strip() if len(row) > 16 else ""
                district = str(row[17] or "").strip() if len(row) > 17 else ""
                address_detail = str(row[18] or "").strip() if len(row) > 18 else ""
                full_living_address = str(row[22] or "").strip() if len(row) > 22 else ""
                living_address = str(row[21] or "").strip() if len(row) > 21 else ""
                commute = str(row[23] or "").strip() if len(row) > 23 else ""
                
                # Build address
                address_parts = [p for p in [country, region, district, address_detail] if p]
                full_address = ", ".join(address_parts) if address_parts else full_living_address or living_address
                
                # Parse birth_date
                parsed_birth_date = None
                if birth_date:
                    if isinstance(birth_date, datetime):
                        parsed_birth_date = birth_date.date()
                    elif isinstance(birth_date, date):
                        parsed_birth_date = birth_date
                    elif isinstance(birth_date, str):
                        for fmt in ["%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"]:
                            try:
                                parsed_birth_date = datetime.strptime(birth_date, fmt).date()
                                break
                            except Exception:
                                pass  # Expected: trying multiple date formats
                
                # Parse course
                course_num = 1
                if course:
                    if isinstance(course, (int, float)):
                        course_num = int(course)
                    elif isinstance(course, str):
                        match = re.search(r'(\d+)', str(course))
                        if match:
                            course_num = int(match.group(1))
                
                # Handle group - check cache first
                group_id = None
                if group_name:
                    if group_name in groups_cache:
                        group_id = groups_cache[group_name]
                    elif group_name in groups_to_create:
                        group_id = f"__new__{group_name}"  # Placeholder
                    else:
                        # Mark for creation
                        groups_to_create[group_name] = {
                            "name": group_name,
                            "faculty": specialty_name or "Unknown",
                            "course_year": course_num,
                            "is_active": True
                        }
                        group_id = f"__new__{group_name}"  # Placeholder
                
                # Add student to batch
                students_to_create.append({
                    "student_id": student_id,
                    "name": full_name,
                    "phone": phone or None,
                    "passport": passport or None,
                    "jshshir": jshshir or None,
                    "birth_date": parsed_birth_date,
                    "address": full_address or None,
                    "commute": commute or None,
                    "group_id": group_id,  # Will be resolved after groups created
                    "is_active": True,
                    "contract_amount": 0,
                    "contract_paid": 0
                })
                existing_student_ids.add(student_id)
                imported += 1
                
                # Add user to batch
                if create_users and student_id not in existing_user_logins:
                    users_to_create.append({
                        "login": student_id,
                        "password_hash": hashed_password,
                        "name": full_name,
                        "phone": phone or None,
                        "role": UserRole.STUDENT,
                        "is_active": True,
                        "is_first_login": True
                    })
                    student_user_links.append(student_id)
                    existing_user_logins.add(student_id)
                    users_created += 1
                    
            except Exception as e:
                failed += 1
                errors.append({
                    "row": row_idx,
                    "student_id": str(row[0] if row and len(row) > 0 else ""),
                    "name": str(row[1] if row and len(row) > 1 else ""),
                    "error": str(e)
                })
        
        wb.close()
        
        # Now batch insert everything
        
        # 1. Create all new groups first
        if groups_to_create:
            for group_data in groups_to_create.values():
                group = Group(**group_data)
                self.db.add(group)
            await self.db.flush()
            
            # Refresh groups cache
            groups_result = await self.db.execute(select(Group.id, Group.name))
            groups_cache = {row[1]: row[0] for row in groups_result.fetchall()}
        
        # 2. Resolve group_id placeholders and create students
        for student_data in students_to_create:
            group_id = student_data["group_id"]
            if isinstance(group_id, str) and group_id.startswith("__new__"):
                group_name = group_id[7:]  # Remove "__new__" prefix
                student_data["group_id"] = groups_cache.get(group_name)
            
            student = Student(**student_data)
            self.db.add(student)
        
        # 3. Create all users
        for user_data in users_to_create:
            user = User(**user_data)
            self.db.add(user)
        
        # 4. Commit everything at once
        await self.db.commit()
        
        # 5. Link users to students (optional, can be done in bulk later)
        if student_user_links:
            # Get all created users and students
            users_result = await self.db.execute(
                select(User.id, User.login).where(User.login.in_(student_user_links))
            )
            user_id_map = {row[1]: row[0] for row in users_result.fetchall()}
            
            students_result = await self.db.execute(
                select(Student.id, Student.student_id).where(Student.student_id.in_(student_user_links))
            )
            
            for student_id, student_sid in students_result.fetchall():
                if student_sid in user_id_map:
                    await self.db.execute(
                        Student.__table__.update()
                        .where(Student.id == student_id)
                        .values(user_id=user_id_map[student_sid])
                    )
            
            await self.db.commit()
        
        return {
            "success": True,
            "imported": imported,
            "updated": updated,
            "skipped": skipped,
            "failed": failed,
            "users_created": users_created,
            "errors": errors[:50],  # Limit errors to 50
            "message": f"Kontingentdan {imported} ta yangi talaba import qilindi, {updated} ta yangilandi, {users_created} ta foydalanuvchi yaratildi."
        }
