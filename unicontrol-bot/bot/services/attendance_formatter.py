from typing import List, Dict, Any, Optional
from datetime import datetime


class AttendanceFormatter:
    """
    Formats attendance data for Telegram messages.
    Creates beautiful, readable messages in Uzbek.
    """
    
    # Status emojis
    STATUS_EMOJI = {
        "present": "✅",
        "late": "⚠️",
        "absent": "❌",
        "excused": "📋"
    }
    
    # Status text in Uzbek
    STATUS_TEXT = {
        "present": "Keldi",
        "late": "Kech qoldi",
        "absent": "Kelmadi",
        "excused": "Sababli"
    }
    
    @classmethod
    def format_single_attendance(
        cls,
        attendance: Dict[str, Any],
        include_group: bool = False
    ) -> str:
        """
        Format single attendance record.
        
        Args:
            attendance: Attendance record from API
            include_group: Include group info in message
            
        Returns:
            Formatted message string
        """
        student_name = attendance.get("student_name", "Noma'lum")
        status = attendance.get("status", "unknown")
        reason = attendance.get("reason", "")
        lesson = attendance.get("lesson_number", "")
        date_str = attendance.get("date", "")
        group_code = attendance.get("group_code", "")
        
        emoji = cls.STATUS_EMOJI.get(status, "❓")
        status_text = cls.STATUS_TEXT.get(status, status)
        
        # Format date
        if date_str:
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                date_formatted = dt.strftime("%d.%m.%Y")
            except:
                date_formatted = date_str
        else:
            date_formatted = datetime.now().strftime("%d.%m.%Y")
        
        # Build message
        lines = [
            f"👤 <b>{student_name}</b>",
            f"📅 {date_formatted}" + (f" | {lesson}-para" if lesson else ""),
            f"⏰ Holat: {emoji} <b>{status_text}</b>"
        ]
        
        if reason:
            lines.append(f"📝 Sabab: {reason}")
        
        if include_group and group_code:
            lines.insert(0, f"🏫 Guruh: <b>{group_code}</b>")
        
        return "\n".join(lines)
    
    @classmethod
    def format_attendance_update(
        cls,
        attendance: Dict[str, Any],
        group_code: str
    ) -> str:
        """
        Format attendance update notification.
        
        Args:
            attendance: Attendance record
            group_code: Academic group code
            
        Returns:
            Formatted notification message
        """
        status = attendance.get("status", "unknown")
        emoji = cls.STATUS_EMOJI.get(status, "❓")
        
        header = f"📋 <b>Davomat yangilandi - {group_code}</b>\n"
        header += "━" * 20 + "\n\n"
        
        body = cls.format_single_attendance(attendance)
        
        footer = "\n\n" + "━" * 20
        
        return header + body + footer
    
    @classmethod
    def format_group_attendance(
        cls,
        attendances: List[Dict[str, Any]],
        group_code: str,
        date_str: Optional[str] = None
    ) -> str:
        """
        Format group attendance summary.
        
        Args:
            attendances: List of attendance records
            group_code: Academic group code
            date_str: Date string
            
        Returns:
            Formatted summary message
        """
        if not attendances:
            return f"📋 <b>{group_code}</b> - Bugun davomat ma'lumoti yo'q"
        
        # Count by status
        stats = {"present": 0, "late": 0, "absent": 0, "excused": 0}
        for att in attendances:
            status = att.get("status", "unknown")
            if status in stats:
                stats[status] += 1
        
        total = len(attendances)
        date_formatted = date_str or datetime.now().strftime("%d.%m.%Y")
        
        # Header
        lines = [
            f"📋 <b>Davomat - {group_code}</b>",
            f"📅 {date_formatted}",
            "━" * 22,
            "",
            "📊 <b>Umumiy statistika:</b>",
            f"  {cls.STATUS_EMOJI['present']} Keldi: {stats['present']}",
            f"  {cls.STATUS_EMOJI['late']} Kech qoldi: {stats['late']}",
            f"  {cls.STATUS_EMOJI['absent']} Kelmadi: {stats['absent']}",
            f"  {cls.STATUS_EMOJI['excused']} Sababli: {stats['excused']}",
            f"  👥 Jami: {total}",
            "",
            "━" * 22
        ]
        
        # List late and absent students
        late_students = [a for a in attendances if a.get("status") == "late"]
        absent_students = [a for a in attendances if a.get("status") == "absent"]
        
        if late_students:
            lines.append("")
            lines.append(f"⚠️ <b>Kech qolganlar ({len(late_students)}):</b>")
            for att in late_students[:10]:  # Limit to 10
                name = att.get("student_name", "")
                reason = att.get("reason", "")
                line = f"  • {name}"
                if reason:
                    line += f" - <i>{reason}</i>"
                lines.append(line)
            if len(late_students) > 10:
                lines.append(f"  ... va yana {len(late_students) - 10} ta")
        
        if absent_students:
            lines.append("")
            lines.append(f"❌ <b>Kelmaganlar ({len(absent_students)}):</b>")
            for att in absent_students[:10]:  # Limit to 10
                name = att.get("student_name", "")
                reason = att.get("reason", "")
                line = f"  • {name}"
                if reason:
                    line += f" - <i>{reason}</i>"
                lines.append(line)
            if len(absent_students) > 10:
                lines.append(f"  ... va yana {len(absent_students) - 10} ta")
        
        return "\n".join(lines)
    
    @classmethod
    def format_student_attendance_summary(
        cls,
        attendances: List[Dict[str, Any]],
        student_name: str,
        period: str = "bu hafta"
    ) -> str:
        """
        Format student personal attendance summary.
        
        Args:
            attendances: List of student's attendance records
            student_name: Student name
            period: Period description
            
        Returns:
            Formatted summary
        """
        if not attendances:
            return f"👤 <b>{student_name}</b>\n📋 {period.capitalize()} davomat ma'lumoti yo'q"
        
        # Count by status
        stats = {"present": 0, "late": 0, "absent": 0, "excused": 0}
        for att in attendances:
            status = att.get("status", "unknown")
            if status in stats:
                stats[status] += 1
        
        total = len(attendances)
        present_percent = round((stats["present"] + stats["excused"]) / total * 100) if total > 0 else 0
        
        lines = [
            f"👤 <b>{student_name}</b>",
            f"📅 Davr: {period}",
            "━" * 22,
            "",
            f"📊 <b>Davomat statistikasi:</b>",
            f"  {cls.STATUS_EMOJI['present']} Keldi: {stats['present']}",
            f"  {cls.STATUS_EMOJI['late']} Kech qoldi: {stats['late']}",
            f"  {cls.STATUS_EMOJI['absent']} Kelmadi: {stats['absent']}",
            f"  {cls.STATUS_EMOJI['excused']} Sababli: {stats['excused']}",
            "",
            f"📈 <b>Davomat foizi: {present_percent}%</b>",
            "━" * 22
        ]
        
        # Recent issues
        recent_issues = [
            a for a in sorted(attendances, key=lambda x: x.get("date", ""), reverse=True)
            if a.get("status") in ("late", "absent")
        ][:5]
        
        if recent_issues:
            lines.append("")
            lines.append("⚠️ <b>So'nggi muammolar:</b>")
            for att in recent_issues:
                date_str = att.get("date", "")
                status = att.get("status", "")
                emoji = cls.STATUS_EMOJI.get(status, "")
                status_text = cls.STATUS_TEXT.get(status, status)
                
                try:
                    dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    date_formatted = dt.strftime("%d.%m")
                except:
                    date_formatted = date_str[:5]
                
                lines.append(f"  • {date_formatted}: {emoji} {status_text}")
        
        return "\n".join(lines)
    
    @classmethod
    def format_group_info(cls, group: Dict[str, Any]) -> str:
        """
        Format group information.
        
        Args:
            group: Group data from API
            
        Returns:
            Formatted group info
        """
        code = group.get("code", "")
        name = group.get("name", "")
        faculty = group.get("faculty", "")
        course = group.get("course", "")
        student_count = group.get("student_count", 0)
        leader = group.get("leader_name", "")
        
        lines = [
            f"🏫 <b>Guruh: {code}</b>",
            "━" * 20
        ]
        
        if name:
            lines.append(f"📝 Nomi: {name}")
        if faculty:
            lines.append(f"🎓 Fakultet: {faculty}")
        if course:
            lines.append(f"📚 Kurs: {course}")
        if student_count:
            lines.append(f"👥 Talabalar: {student_count} ta")
        if leader:
            lines.append(f"👤 Sardor: {leader}")
        
        lines.append("━" * 20)
        
        return "\n".join(lines)
    
    @classmethod
    def format_search_results(
        cls,
        groups: List[Dict[str, Any]],
        query: str
    ) -> str:
        """
        Format group search results.
        
        Args:
            groups: List of groups from search
            query: Search query
            
        Returns:
            Formatted results
        """
        if not groups:
            return f"🔍 <b>\"{query}\"</b> bo'yicha guruh topilmadi"
        
        lines = [
            f"🔍 <b>\"{query}\"</b> bo'yicha natijalar:",
            "━" * 22,
            ""
        ]
        
        for i, group in enumerate(groups[:10], 1):
            code = group.get("code", "")
            name = group.get("name", "")
            student_count = group.get("student_count", 0)
            
            line = f"{i}. <b>{code}</b>"
            if name:
                line += f" - {name}"
            if student_count:
                line += f" ({student_count} ta)"
            lines.append(line)
        
        if len(groups) > 10:
            lines.append(f"\n... va yana {len(groups) - 10} ta guruh")
        
        lines.append("")
        lines.append("💡 <i>Obuna bo'lish uchun: /subscribe [kod]</i>")
        
        return "\n".join(lines)
