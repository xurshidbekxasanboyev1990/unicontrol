"""
UniControl - AI Schedule Import Agent
======================================
Intelligent AI agent that enhances Excel schedule import:

1. Smart Group Matching — Uses GPT to match Excel group names to DB groups
   even when names differ significantly (abbreviations, typos, different formats)

2. Smart Cell Parsing — When regex fails, AI parses messy cell content
   to extract subject, type, teacher, room, building

3. Bulk Processing — Sends all unmatched data in one API call for efficiency

Author: UniControl Team
Version: 1.0.0
"""

import json
import re
from typing import Optional, List, Dict, Any, Tuple
from loguru import logger

import openai
from app.config import settings
from app.models.schedule import ScheduleType, WeekDay


class AIScheduleAgent:
    """
    AI agent for intelligent schedule import matching.
    Uses OpenAI GPT-4o-mini for smart matching when fuzzy/regex fails.
    """

    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
        self.model = settings.OPENAI_MODEL or "gpt-4o-mini"
        self.total_tokens_used = 0

    def is_available(self) -> bool:
        """Check if AI is available (API key configured)."""
        return self.client is not None

    async def _call_openai(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.1,
    ) -> Optional[str]:
        """Call OpenAI API and return content. Returns None on failure."""
        if not self.client:
            return None

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )

            self.total_tokens_used += response.usage.total_tokens
            content = response.choices[0].message.content
            logger.info(
                f"AI Schedule Agent: {response.usage.total_tokens} tokens used "
                f"(total: {self.total_tokens_used})"
            )
            return content

        except Exception as e:
            logger.error(f"AI Schedule Agent OpenAI call failed: {e}")
            return None

    # ═══════════════════════════════════════════════════════
    # 1. SMART GROUP MATCHING
    # ═══════════════════════════════════════════════════════

    async def match_groups(
        self,
        excel_groups: List[str],
        db_groups: List[str],
    ) -> Dict[str, Optional[str]]:
        """
        Use AI to match Excel group names to database group names.

        Args:
            excel_groups: Group names found in Excel file
            db_groups: Group names existing in database

        Returns:
            Dict mapping excel_name -> db_name (or None if no match)
        """
        if not excel_groups or not db_groups:
            return {}

        if not self.is_available():
            logger.warning("AI not available for group matching")
            return {}

        system_prompt = """Sen O'zbekiston universitetlari uchun guruh nomlarini moslashtiradigan AI agentsan.

Senga Excel fayldagi guruh nomlari va bazadagi guruh nomlari beriladi.
Vazifang: har bir Excel guruh nomini bazadagi eng mos guruhga birlashtirish.

MUHIM QOIDALAR:
1. Guruh nomlari turli formatlarda bo'lishi mumkin:
   - KI-25-09, KI_25_09, KI 25 09, КИ-25-09 (kirill)
   - PM-1-01, PM_1_01, ПМ-1-01
   - AT25-01, AT-25-01
   - 1-KI-25, KI25-09
   - Qisqartirilgan: KI → Kompyuter injiniringi
   
2. Agar ishonchli mos kelsa — match qil
3. Agar ishonchsiz bo'lsa — null qo'y
4. Faqat bitta eng yaxshi matchni tanlash kerak
5. Kirill va lotin alifbolarini ham inobatga ol (КИ = KI, ПМ = PM)
6. Raqamlar muhim — 25-09 va 25-10 turli guruhlar!

JSON formatda javob ber:
{
  "matches": {
    "excel_guruh_nomi": "bazadagi_guruh_nomi yoki null"
  }
}"""

        user_prompt = f"""Excel fayldagi guruh nomlari:
{json.dumps(excel_groups, ensure_ascii=False)}

Bazadagi guruh nomlari:
{json.dumps(db_groups, ensure_ascii=False)}

Har bir Excel guruh nomini bazadagi eng mos guruhga moslashtir. Agar mos kelmasa null qo'y."""

        content = await self._call_openai(system_prompt, user_prompt, max_tokens=4000)
        if not content:
            return {}

        try:
            result = json.loads(content)
            matches = result.get("matches", {})

            # Validate: ensure matched names actually exist in db_groups
            db_set = set(db_groups)
            validated = {}
            for excel_name, db_name in matches.items():
                if db_name and db_name in db_set:
                    validated[excel_name] = db_name
                else:
                    validated[excel_name] = None

            ai_matched = sum(1 for v in validated.values() if v is not None)
            logger.info(
                f"AI Group Matching: {ai_matched}/{len(excel_groups)} "
                f"guruh moslashtirildi"
            )
            return validated

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"AI group matching response parse error: {e}")
            return {}

    # ═══════════════════════════════════════════════════════
    # 2. SMART CELL CONTENT PARSING
    # ═══════════════════════════════════════════════════════

    async def parse_cells(
        self,
        cells: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Use AI to parse messy schedule cell contents that regex couldn't handle.

        Args:
            cells: List of dicts with keys: "id" (row-col ref), "content" (raw text)

        Returns:
            List of parsed dicts with keys:
            id, subject, schedule_type, teacher, room, building
        """
        if not cells:
            return []

        if not self.is_available():
            return []

        # Process in batches of 50 to avoid token limits
        all_results = []
        batch_size = 50

        for i in range(0, len(cells), batch_size):
            batch = cells[i : i + batch_size]
            batch_results = await self._parse_cells_batch(batch)
            all_results.extend(batch_results)

        return all_results

    async def _parse_cells_batch(
        self,
        cells: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """Parse a batch of cells using AI."""

        system_prompt = """Sen O'zbekiston universitetlari dars jadvali hujayralarini tahlil qiladigan AI agentsan.

Senga dars jadvali katakchalari (cell) matni beriladi. Vazifang har biridan quyidagilarni ajratib olish:
- subject: fan nomi
- schedule_type: dars turi (lecture, practice, lab, seminar, exam, consultation)
- teacher: o'qituvchi ismi
- room: xona raqami
- building: bino (A bino, B bino va h.k.)

QOIDALAR:
1. Fan nomi — odatda birinchi keladi
2. Qavslar ichidagi so'z — dars turi: (ma'ruza)=lecture, (amaliy)=practice, (lab)=lab, (seminar)=seminar, (imtihon)=exam
3. O'qituvchi — odatda "Familiya I.O." yoki "Familiya Ism Otasining ismi" formatda
4. Xona — raqam + "xona" yoki faqat raqam: "307-xona", "Aud.305", "L-2"
5. Bino — "A bino", "B bino", "Asosiy bino"
6. Agar aniqlab bo'lmasa — null qo'y
7. Ma'lumot bo'sh yoki "-" bo'lsa — hamma narsani null qo'y

JSON formatda javob ber:
{
  "parsed": [
    {
      "id": "cell_id",
      "subject": "fan nomi yoki null",
      "schedule_type": "lecture|practice|lab|seminar|exam|consultation",
      "teacher": "o'qituvchi ismi yoki null",
      "room": "xona yoki null",
      "building": "bino yoki null"
    }
  ]
}"""

        cells_text = json.dumps(cells, ensure_ascii=False, indent=2)
        user_prompt = f"""Quyidagi dars jadvali katakchalarini tahlil qil:

{cells_text}

Har bir katakchadan fan, tur, o'qituvchi, xona, binoni ajrat."""

        content = await self._call_openai(system_prompt, user_prompt, max_tokens=4000)
        if not content:
            return []

        try:
            result = json.loads(content)
            parsed = result.get("parsed", [])

            # Validate schedule_type values
            valid_types = {
                "lecture": ScheduleType.LECTURE,
                "practice": ScheduleType.PRACTICE,
                "lab": ScheduleType.LAB,
                "seminar": ScheduleType.SEMINAR,
                "exam": ScheduleType.EXAM,
                "consultation": ScheduleType.CONSULTATION,
            }

            for item in parsed:
                stype = item.get("schedule_type", "lecture")
                if stype not in valid_types:
                    item["schedule_type"] = "lecture"

            logger.info(f"AI Cell Parsing: {len(parsed)} cells parsed")
            return parsed

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"AI cell parsing response parse error: {e}")
            return []

    # ═══════════════════════════════════════════════════════
    # 3. FULL SCHEDULE ANALYSIS
    # ═══════════════════════════════════════════════════════

    async def analyze_schedule_data(
        self,
        records: List[Dict[str, Any]],
        db_groups: List[str],
    ) -> Dict[str, Any]:
        """
        Full AI analysis of parsed schedule data:
        - Fix unmatched groups
        - Detect and fix anomalies (duplicate lessons, wrong times)
        - Suggest corrections

        Args:
            records: Parsed schedule records
            db_groups: Available group names in DB

        Returns:
            Analysis report with suggestions
        """
        if not self.is_available() or not records:
            return {"suggestions": [], "anomalies": []}

        # Collect stats for AI
        unmatched = set()
        matched = set()
        subjects = set()
        teachers = set()

        for rec in records:
            if rec.get("group_id"):
                matched.add(rec.get("db_group_name", ""))
            else:
                unmatched.add(rec.get("sheet_group_name", ""))
            if rec.get("subject"):
                subjects.add(rec["subject"])
            if rec.get("teacher"):
                teachers.add(rec["teacher"])

        system_prompt = """Sen O'zbekiston universitetlari dars jadvali tahlilchisisisan.

Senga import qilingan jadval statistikasi beriladi. Vazifang:
1. Xatoliklarni topish (bir vaqtda 2 ta dars, noto'g'ri vaqtlar)
2. Takliflar berish (guruh moslashmaslari, tipik xatolar)
3. Umumiy sifat baholash

JSON formatda javob ber:
{
  "quality_score": 1-10,
  "anomalies": ["xatolik tavsifi"],
  "suggestions": ["taklif"],
  "summary": "umumiy xulosa"
}"""

        stats = {
            "total_records": len(records),
            "matched_groups": list(matched),
            "unmatched_groups": list(unmatched),
            "unique_subjects": len(subjects),
            "unique_teachers": len(teachers),
            "available_db_groups": db_groups[:50],  # limit to avoid token overflow
            "sample_subjects": list(subjects)[:20],
            "sample_teachers": list(teachers)[:20],
        }

        user_prompt = f"""Import qilingan jadval statistikasi:

{json.dumps(stats, ensure_ascii=False, indent=2)}

Tahlil qil va takliflar ber."""

        content = await self._call_openai(
            system_prompt, user_prompt, max_tokens=2000
        )
        if not content:
            return {"suggestions": [], "anomalies": [], "quality_score": 0}

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"suggestions": [], "anomalies": [], "quality_score": 0}

    # ═══════════════════════════════════════════════════════
    # 4. MASTER IMPORT PIPELINE
    # ═══════════════════════════════════════════════════════

    async def enhance_import(
        self,
        records: List[Dict[str, Any]],
        db_group_names: List[str],
        group_lookup: Dict[str, Any],
        group_name_map: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Master AI enhancement pipeline for schedule import.
        Called after initial regex-based parsing.

        Steps:
        1. Collect all unmatched groups → AI match
        2. Collect all unparsed/empty cells → AI parse
        3. Apply AI results back to records
        4. Run quality analysis

        Returns:
            {
                "records": enhanced records,
                "ai_matched_groups": {excel_name: db_name},
                "ai_parsed_cells": count,
                "analysis": quality analysis,
                "tokens_used": total tokens
            }
        """
        if not self.is_available():
            logger.info("AI not available, skipping enhancement")
            return {
                "records": records,
                "ai_matched_groups": {},
                "ai_parsed_cells": 0,
                "analysis": None,
                "tokens_used": 0,
            }

        logger.info(f"AI Schedule Agent: enhancing {len(records)} records...")

        # ── Step 1: Match unmatched groups ──
        unmatched_groups = list(set(
            rec["sheet_group_name"]
            for rec in records
            if not rec.get("group_id") and rec.get("sheet_group_name")
        ))

        ai_group_matches = {}
        if unmatched_groups and db_group_names:
            logger.info(
                f"AI: {len(unmatched_groups)} unmatched groups to resolve..."
            )
            ai_group_matches = await self.match_groups(
                unmatched_groups, db_group_names
            )

            # Apply AI group matches to records
            for rec in records:
                if not rec.get("group_id") and rec.get("sheet_group_name"):
                    excel_name = rec["sheet_group_name"]
                    db_name = ai_group_matches.get(excel_name)
                    if db_name and db_name in group_lookup:
                        rec["group_id"] = group_lookup[db_name].id
                        rec["db_group_name"] = db_name
                        group_name_map[excel_name] = db_name

        # ── Step 2: Parse cells where subject is missing ──
        unparsed_cells = []
        for i, rec in enumerate(records):
            if not rec.get("subject") and rec.get("_raw_cell"):
                unparsed_cells.append({
                    "id": str(i),
                    "content": rec["_raw_cell"],
                })

        ai_parsed_count = 0
        if unparsed_cells:
            logger.info(f"AI: {len(unparsed_cells)} unparsed cells to resolve...")
            parsed_results = await self.parse_cells(unparsed_cells)

            # Build lookup by id
            parsed_map = {p["id"]: p for p in parsed_results}

            type_map = {
                "lecture": ScheduleType.LECTURE,
                "practice": ScheduleType.PRACTICE,
                "lab": ScheduleType.LAB,
                "seminar": ScheduleType.SEMINAR,
                "exam": ScheduleType.EXAM,
                "consultation": ScheduleType.CONSULTATION,
            }

            for i, rec in enumerate(records):
                sid = str(i)
                if sid in parsed_map:
                    p = parsed_map[sid]
                    if p.get("subject"):
                        rec["subject"] = p["subject"]
                        rec["schedule_type"] = type_map.get(
                            p.get("schedule_type", "lecture"),
                            ScheduleType.LECTURE,
                        )
                        if p.get("teacher"):
                            rec["teacher"] = p["teacher"]
                        if p.get("room"):
                            rec["room"] = p["room"]
                        if p.get("building"):
                            rec["building"] = p["building"]
                        ai_parsed_count += 1

        # ── Step 3: Quality analysis ──
        analysis = await self.analyze_schedule_data(records, db_group_names)

        result = {
            "records": records,
            "ai_matched_groups": {
                k: v for k, v in ai_group_matches.items() if v is not None
            },
            "ai_parsed_cells": ai_parsed_count,
            "analysis": analysis,
            "tokens_used": self.total_tokens_used,
        }

        logger.info(
            f"AI Schedule Agent complete: "
            f"{len(result['ai_matched_groups'])} groups matched, "
            f"{ai_parsed_count} cells parsed, "
            f"{self.total_tokens_used} tokens used"
        )

        return result
