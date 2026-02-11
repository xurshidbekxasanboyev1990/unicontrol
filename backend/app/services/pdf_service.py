"""
UniControl - PDF Report Generator
==================================
Generates professional PDF reports for attendance, payment, students, and groups.

Author: UniControl Team
Version: 1.0.0
"""

import io
from datetime import date, datetime
from app.config import now_tashkent
from typing import Optional, List
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from loguru import logger

from app.models.student import Student
from app.models.group import Group
from app.models.attendance import Attendance, AttendanceStatus
from app.models.report import Report, ReportType


class PDFReportGenerator:
    """Professional PDF report generator for UniControl."""

    # Colors
    PRIMARY = colors.HexColor("#6D28D9")       # Violet
    PRIMARY_LIGHT = colors.HexColor("#EDE9FE")  # Light violet
    HEADER_BG = colors.HexColor("#1E293B")      # Slate-800
    SUCCESS = colors.HexColor("#059669")         # Emerald
    WARNING = colors.HexColor("#D97706")         # Amber
    DANGER = colors.HexColor("#DC2626")          # Red
    TEXT_DARK = colors.HexColor("#1E293B")
    TEXT_GRAY = colors.HexColor("#64748B")
    BORDER = colors.HexColor("#E2E8F0")
    ROW_ALT = colors.HexColor("#F8FAFC")

    def __init__(self, db: AsyncSession):
        self.db = db
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='DocTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            textColor=self.HEADER_BG,
            spaceAfter=6,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name='DocSubtitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.TEXT_GRAY,
            spaceAfter=20,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.PRIMARY,
            spaceBefore=16,
            spaceAfter=8,
        ))
        self.styles.add(ParagraphStyle(
            name='InfoLabel',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.TEXT_GRAY,
        ))
        self.styles.add(ParagraphStyle(
            name='InfoValue',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.TEXT_DARK,
            fontName='Helvetica-Bold',
        ))
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name='TableCell',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=self.TEXT_DARK,
        ))
        self.styles.add(ParagraphStyle(
            name='TableCellCenter',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=self.TEXT_DARK,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name='FooterText',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=self.TEXT_GRAY,
            alignment=TA_CENTER,
        ))

    def _header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()
        width, height = A4

        # Header line
        canvas.setStrokeColor(self.PRIMARY)
        canvas.setLineWidth(2)
        canvas.line(20 * mm, height - 15 * mm, width - 20 * mm, height - 15 * mm)

        # Header text
        canvas.setFont("Helvetica-Bold", 10)
        canvas.setFillColor(self.HEADER_BG)
        canvas.drawString(20 * mm, height - 13 * mm, "UniControl")

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(self.TEXT_GRAY)
        now = now_tashkent().strftime("%d.%m.%Y %H:%M")
        canvas.drawRightString(width - 20 * mm, height - 13 * mm, f"Yaratilgan: {now}")

        # Footer
        canvas.setStrokeColor(self.BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(20 * mm, 12 * mm, width - 20 * mm, 12 * mm)

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(self.TEXT_GRAY)
        canvas.drawString(20 * mm, 8 * mm, "UniControl - University Control System")
        canvas.drawRightString(width - 20 * mm, 8 * mm, f"Sahifa {doc.page}")

        canvas.restoreState()

    def _build_info_table(self, info_pairs: list) -> Table:
        """Build a styled info key-value table."""
        data = []
        for label, value in info_pairs:
            data.append([
                Paragraph(label, self.styles['InfoLabel']),
                Paragraph(str(value) if value else "—", self.styles['InfoValue']),
            ])
        
        t = Table(data, colWidths=[55 * mm, 100 * mm])
        t.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, self.BORDER),
        ]))
        return t

    def _build_data_table(self, headers: list, rows: list, col_widths=None) -> Table:
        """Build a professional styled data table."""
        # Header row
        header_row = [Paragraph(h, self.styles['TableHeader']) for h in headers]
        
        # Data rows  
        styled_rows = [header_row]
        for row in rows:
            styled_rows.append([
                Paragraph(str(cell) if cell is not None else "—", self.styles['TableCellCenter'])
                for cell in row
            ])

        t = Table(styled_rows, colWidths=col_widths, repeatRows=1)
        
        style_commands = [
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.HEADER_BG),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Data
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, self.BORDER),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, self.PRIMARY),
        ]
        
        # Alternating row colors
        for i in range(1, len(styled_rows)):
            if i % 2 == 0:
                style_commands.append(('BACKGROUND', (0, i), (-1, i), self.ROW_ALT))
        
        t.setStyle(TableStyle(style_commands))
        return t

    def _build_summary_cards(self, cards: list) -> Table:
        """Build summary statistic cards."""
        data = []
        for title, value, color in cards:
            data.append([
                Paragraph(f'<font size="16" color="{color}"><b>{value}</b></font><br/>'
                         f'<font size="8" color="#64748B">{title}</font>',
                         self.styles['TableCellCenter'])
            ])
        
        # Horizontal layout
        row = [d[0] for d in data]
        t = Table([row], colWidths=[38 * mm] * len(row))
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, self.BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, self.BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        return t

    # ═══════════════════════════════════════════
    # ATTENDANCE REPORT
    # ═══════════════════════════════════════════
    async def generate_attendance_report(
        self, report: Report
    ) -> bytes:
        """Generate attendance report PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            topMargin=22 * mm, bottomMargin=18 * mm,
            leftMargin=20 * mm, rightMargin=20 * mm,
        )
        elements = []

        # Title
        elements.append(Paragraph("DAVOMAT HISOBOTI", self.styles['DocTitle']))
        subtitle = f"Davr: {self._fmt_date(report.date_from)} — {self._fmt_date(report.date_to)}"
        elements.append(Paragraph(subtitle, self.styles['DocSubtitle']))
        elements.append(HRFlowable(width="100%", thickness=1, color=self.PRIMARY))
        elements.append(Spacer(1, 8 * mm))

        # Get group info
        group = None
        group_name = "Barcha guruhlar"
        if report.group_id:
            result = await self.db.execute(select(Group).where(Group.id == report.group_id))
            group = result.scalar_one_or_none()
            if group:
                group_name = group.name

        # Info block
        elements.append(self._build_info_table([
            ("Hisobot turi:", "Davomat"),
            ("Guruh:", group_name),
            ("Davr:", subtitle.replace("Davr: ", "")),
            ("Holati:", report.status.value.upper()),
            ("Yaratuvchi ID:", str(report.created_by)),
        ]))
        elements.append(Spacer(1, 8 * mm))

        # Fetch attendance data
        query = select(Attendance)
        if report.date_from:
            query = query.where(Attendance.date >= report.date_from)
        if report.date_to:
            query = query.where(Attendance.date <= report.date_to)
        if report.group_id:
            query = query.join(Student, Student.id == Attendance.student_id).where(
                Student.group_id == report.group_id
            )
        query = query.order_by(Attendance.date.desc())
        
        result = await self.db.execute(query)
        attendances = result.scalars().all()

        total = len(attendances)
        present = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        absent = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
        late = sum(1 for a in attendances if a.status == AttendanceStatus.LATE)

        # Summary cards
        elements.append(Paragraph("Umumiy ko'rsatkichlar", self.styles['SectionTitle']))
        elements.append(self._build_summary_cards([
            ("Jami yozuvlar", str(total), "#6D28D9"),
            ("Keldi", str(present), "#059669"),
            ("Kelmadi", str(absent), "#DC2626"),
            ("Kechikdi", str(late), "#D97706"),
            ("Davomat %", f"{round(present/total*100, 1) if total > 0 else 0}%", "#2563EB"),
        ]))
        elements.append(Spacer(1, 8 * mm))

        # Students breakdown
        if report.group_id:
            students_result = await self.db.execute(
                select(Student).where(
                    Student.group_id == report.group_id,
                    Student.is_active == True
                ).order_by(Student.name)
            )
            students = students_result.scalars().all()

            elements.append(Paragraph("Talabalar bo'yicha davomat", self.styles['SectionTitle']))
            
            rows = []
            for idx, student in enumerate(students, 1):
                # Get this student's attendance in the period
                s_query = select(Attendance).where(
                    Attendance.student_id == student.id
                )
                if report.date_from:
                    s_query = s_query.where(Attendance.date >= report.date_from)
                if report.date_to:
                    s_query = s_query.where(Attendance.date <= report.date_to)
                s_result = await self.db.execute(s_query)
                s_att = s_result.scalars().all()
                
                s_total = len(s_att)
                s_present = sum(1 for a in s_att if a.status == AttendanceStatus.PRESENT)
                s_absent = sum(1 for a in s_att if a.status == AttendanceStatus.ABSENT)
                s_late = sum(1 for a in s_att if a.status == AttendanceStatus.LATE)
                s_rate = f"{round(s_present/s_total*100, 1)}%" if s_total > 0 else "—"
                
                rows.append([
                    str(idx), student.name, str(s_total),
                    str(s_present), str(s_absent), str(s_late), s_rate
                ])

            if rows:
                elements.append(self._build_data_table(
                    ["#", "Talaba", "Jami", "Keldi", "Kelmadi", "Kechikdi", "%"],
                    rows,
                    col_widths=[10*mm, 55*mm, 18*mm, 18*mm, 22*mm, 22*mm, 18*mm],
                ))

        elements.append(Spacer(1, 10 * mm))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=self.BORDER))
        elements.append(Spacer(1, 4 * mm))
        elements.append(Paragraph(
            f"Hisobot #{report.id} | UniControl tizimi tomonidan avtomatik yaratildi",
            self.styles['FooterText']
        ))

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        return buffer.getvalue()

    # ═══════════════════════════════════════════
    # PAYMENT REPORT
    # ═══════════════════════════════════════════
    async def generate_payment_report(self, report: Report) -> bytes:
        """Generate payment/contract report PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            topMargin=22 * mm, bottomMargin=18 * mm,
            leftMargin=20 * mm, rightMargin=20 * mm,
        )
        elements = []

        elements.append(Paragraph("KONTRAKT TO'LOV HISOBOTI", self.styles['DocTitle']))
        subtitle = f"Davr: {self._fmt_date(report.date_from)} — {self._fmt_date(report.date_to)}"
        elements.append(Paragraph(subtitle, self.styles['DocSubtitle']))
        elements.append(HRFlowable(width="100%", thickness=1, color=self.PRIMARY))
        elements.append(Spacer(1, 8 * mm))

        # Fetch students
        query = select(Student).where(Student.is_active == True)
        if report.group_id:
            query = query.where(Student.group_id == report.group_id)
        query = query.order_by(Student.name)
        
        result = await self.db.execute(query)
        students = result.scalars().all()

        # Group info
        group_name = "Barcha guruhlar"
        if report.group_id:
            g_result = await self.db.execute(select(Group).where(Group.id == report.group_id))
            g = g_result.scalar_one_or_none()
            if g:
                group_name = g.name

        elements.append(self._build_info_table([
            ("Hisobot turi:", "Kontrakt to'lovlari"),
            ("Guruh:", group_name),
            ("Jami talabalar:", str(len(students))),
            ("Holati:", report.status.value.upper()),
        ]))
        elements.append(Spacer(1, 8 * mm))

        # Calculate totals
        total_contract = sum(float(s.contract_amount or 0) for s in students)
        total_paid = sum(float(s.contract_paid or 0) for s in students)
        total_remaining = total_contract - total_paid
        paid_count = sum(1 for s in students if s.contract_paid >= s.contract_amount and s.contract_amount > 0)
        unpaid_count = len(students) - paid_count

        elements.append(Paragraph("Moliyaviy ko'rsatkichlar", self.styles['SectionTitle']))
        elements.append(self._build_summary_cards([
            ("Jami kontrakt", self._fmt_money(total_contract), "#6D28D9"),
            ("To'langan", self._fmt_money(total_paid), "#059669"),
            ("Qoldiq", self._fmt_money(total_remaining), "#DC2626"),
            ("To'lagan", str(paid_count), "#059669"),
            ("Qarzdor", str(unpaid_count), "#DC2626"),
        ]))
        elements.append(Spacer(1, 8 * mm))

        # Student details
        elements.append(Paragraph("Talabalar bo'yicha to'lov holati", self.styles['SectionTitle']))
        
        rows = []
        for idx, s in enumerate(students, 1):
            amount = float(s.contract_amount or 0)
            paid = float(s.contract_paid or 0)
            remaining = amount - paid
            pct = f"{round(paid/amount*100, 1)}%" if amount > 0 else "—"
            status_text = "To'liq" if remaining <= 0 and amount > 0 else "Qarzdor"
            
            rows.append([
                str(idx), s.name, s.student_id or "—",
                self._fmt_money(amount), self._fmt_money(paid),
                self._fmt_money(max(remaining, 0)), pct, status_text
            ])

        if rows:
            elements.append(self._build_data_table(
                ["#", "Talaba", "ID", "Kontrakt", "To'langan", "Qoldiq", "%", "Holat"],
                rows,
                col_widths=[8*mm, 40*mm, 22*mm, 22*mm, 22*mm, 22*mm, 14*mm, 18*mm],
            ))

        # Totals row
        elements.append(Spacer(1, 4 * mm))
        totals = Table([[
            Paragraph(f"<b>JAMI:</b> Kontrakt: {self._fmt_money(total_contract)} | "
                      f"To'langan: {self._fmt_money(total_paid)} | "
                      f"Qoldiq: {self._fmt_money(total_remaining)}",
                      self.styles['InfoValue'])
        ]], colWidths=[168 * mm])
        totals.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.PRIMARY_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, self.PRIMARY),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(totals)

        elements.append(Spacer(1, 10 * mm))
        elements.append(Paragraph(
            f"Hisobot #{report.id} | UniControl tizimi tomonidan avtomatik yaratildi",
            self.styles['FooterText']
        ))

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        return buffer.getvalue()

    # ═══════════════════════════════════════════
    # STUDENTS REPORT
    # ═══════════════════════════════════════════
    async def generate_students_report(self, report: Report) -> bytes:
        """Generate students list report PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            topMargin=22 * mm, bottomMargin=18 * mm,
            leftMargin=20 * mm, rightMargin=20 * mm,
        )
        elements = []

        elements.append(Paragraph("TALABALAR RO'YXATI HISOBOTI", self.styles['DocTitle']))
        elements.append(HRFlowable(width="100%", thickness=1, color=self.PRIMARY))
        elements.append(Spacer(1, 8 * mm))

        query = select(Student).where(Student.is_active == True)
        if report.group_id:
            query = query.where(Student.group_id == report.group_id)
        query = query.order_by(Student.name)
        
        result = await self.db.execute(query)
        students = result.scalars().all()

        group_name = "Barcha guruhlar"
        if report.group_id:
            g_result = await self.db.execute(select(Group).where(Group.id == report.group_id))
            g = g_result.scalar_one_or_none()
            if g:
                group_name = g.name

        elements.append(self._build_info_table([
            ("Hisobot turi:", "Talabalar ro'yxati"),
            ("Guruh:", group_name),
            ("Jami talabalar:", str(len(students))),
        ]))
        elements.append(Spacer(1, 8 * mm))

        elements.append(Paragraph("Talabalar", self.styles['SectionTitle']))
        
        rows = []
        for idx, s in enumerate(students, 1):
            rows.append([
                str(idx),
                s.name,
                s.student_id or "—",
                s.phone or "—",
                self._fmt_date(s.birth_date),
                "Erkak" if s.gender == "male" else ("Ayol" if s.gender == "female" else "—"),
                self._fmt_date(s.enrollment_date),
            ])

        if rows:
            elements.append(self._build_data_table(
                ["#", "F.I.Sh.", "Talaba ID", "Telefon", "Tug'ilgan sana", "Jinsi", "Qabul sanasi"],
                rows,
                col_widths=[8*mm, 45*mm, 25*mm, 25*mm, 25*mm, 16*mm, 24*mm],
            ))

        elements.append(Spacer(1, 10 * mm))
        elements.append(Paragraph(
            f"Hisobot #{report.id} | Jami: {len(students)} ta talaba | UniControl",
            self.styles['FooterText']
        ))

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        return buffer.getvalue()

    # ═══════════════════════════════════════════
    # GROUPS REPORT
    # ═══════════════════════════════════════════
    async def generate_groups_report(self, report: Report) -> bytes:
        """Generate groups report PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            topMargin=22 * mm, bottomMargin=18 * mm,
            leftMargin=20 * mm, rightMargin=20 * mm,
        )
        elements = []

        elements.append(Paragraph("GURUHLAR HISOBOTI", self.styles['DocTitle']))
        elements.append(HRFlowable(width="100%", thickness=1, color=self.PRIMARY))
        elements.append(Spacer(1, 8 * mm))

        # Fetch all active groups
        result = await self.db.execute(
            select(Group).where(Group.is_active == True).order_by(Group.name)
        )
        groups = result.scalars().all()

        elements.append(self._build_info_table([
            ("Hisobot turi:", "Guruhlar"),
            ("Jami guruhlar:", str(len(groups))),
        ]))
        elements.append(Spacer(1, 8 * mm))

        elements.append(Paragraph("Guruhlar ro'yxati", self.styles['SectionTitle']))
        
        rows = []
        for idx, g in enumerate(groups, 1):
            # Count students
            count_result = await self.db.execute(
                select(func.count(Student.id)).where(
                    Student.group_id == g.id,
                    Student.is_active == True
                )
            )
            student_count = count_result.scalar() or 0
            
            rows.append([
                str(idx),
                g.name,
                getattr(g, 'faculty', '—') or "—",
                str(student_count),
                "Faol" if g.is_active else "Nofaol",
            ])

        if rows:
            elements.append(self._build_data_table(
                ["#", "Guruh nomi", "Fakultet", "Talabalar soni", "Holat"],
                rows,
                col_widths=[10*mm, 50*mm, 50*mm, 30*mm, 25*mm],
            ))

        elements.append(Spacer(1, 10 * mm))
        elements.append(Paragraph(
            f"Hisobot #{report.id} | Jami: {len(groups)} ta guruh | UniControl",
            self.styles['FooterText']
        ))

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        return buffer.getvalue()

    # ═══════════════════════════════════════════
    # GENERIC / CUSTOM REPORT
    # ═══════════════════════════════════════════
    async def generate_generic_report(self, report: Report) -> bytes:
        """Generate a generic/custom report PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            topMargin=22 * mm, bottomMargin=18 * mm,
            leftMargin=20 * mm, rightMargin=20 * mm,
        )
        elements = []

        title = report.name or "HISOBOT"
        elements.append(Paragraph(title.upper(), self.styles['DocTitle']))
        if report.description:
            elements.append(Paragraph(report.description, self.styles['DocSubtitle']))
        elements.append(HRFlowable(width="100%", thickness=1, color=self.PRIMARY))
        elements.append(Spacer(1, 8 * mm))

        group_name = "—"
        if report.group_id:
            g_result = await self.db.execute(select(Group).where(Group.id == report.group_id))
            g = g_result.scalar_one_or_none()
            if g:
                group_name = g.name

        elements.append(self._build_info_table([
            ("Hisobot nomi:", report.name),
            ("Hisobot turi:", report.report_type.value.replace("_", " ").title()),
            ("Format:", report.format.value.upper()),
            ("Guruh:", group_name),
            ("Davr:", f"{self._fmt_date(report.date_from)} — {self._fmt_date(report.date_to)}"),
            ("Holati:", report.status.value.upper()),
            ("Yaratilgan:", self._fmt_datetime(report.created_at)),
        ]))

        if report.ai_result:
            elements.append(Spacer(1, 8 * mm))
            elements.append(Paragraph("AI Tahlil natijasi", self.styles['SectionTitle']))
            elements.append(Paragraph(report.ai_result, self.styles['Normal']))

        elements.append(Spacer(1, 15 * mm))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=self.BORDER))
        elements.append(Spacer(1, 4 * mm))
        elements.append(Paragraph(
            f"Hisobot #{report.id} | UniControl tizimi tomonidan yaratildi",
            self.styles['FooterText']
        ))

        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        return buffer.getvalue()

    # ═══════════════════════════════════════════
    # MAIN DISPATCHER
    # ═══════════════════════════════════════════
    async def generate_pdf(self, report: Report) -> bytes:
        """Generate PDF based on report type."""
        generators = {
            ReportType.ATTENDANCE: self.generate_attendance_report,
            ReportType.PAYMENT: self.generate_payment_report,
            ReportType.STUDENTS: self.generate_students_report,
            ReportType.GROUPS: self.generate_groups_report,
        }
        generator = generators.get(report.report_type, self.generate_generic_report)
        
        logger.info(f"Generating PDF for report #{report.id}, type={report.report_type.value}")
        pdf_data = await generator(report)
        logger.info(f"PDF generated: {len(pdf_data)} bytes for report #{report.id}")
        return pdf_data

    # ═══════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════
    @staticmethod
    def _fmt_date(d) -> str:
        if d is None:
            return "—"
        if isinstance(d, (date, datetime)):
            return d.strftime("%d.%m.%Y")
        return str(d)

    @staticmethod
    def _fmt_datetime(dt) -> str:
        if dt is None:
            return "—"
        if isinstance(dt, datetime):
            return dt.strftime("%d.%m.%Y %H:%M")
        return str(dt)

    @staticmethod
    def _fmt_money(amount) -> str:
        if amount is None:
            return "0"
        return f"{int(amount):,}".replace(",", " ")
