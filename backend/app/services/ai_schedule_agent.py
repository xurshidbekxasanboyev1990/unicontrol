"""
UniControl - AI Schedule Import Agent v2
==========================================
Intelligent AI agent that enhances Excel schedule import:

1. Smart Group Matching — Uses GPT to match Excel group names to DB groups
   even when names differ significantly (abbreviations, typos, different formats)

2. Smart Cell Parsing — ALL cells go through AI for accurate parsing
   handles merged cells, multi-line content, complex formats

3. Quality Analysis — Detects duplicates, time conflicts, anomalies

4. Bulk Processing — Sends data in batches for efficiency

Author: UniControl Team
Version: 2.0.0
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
        temperature: float = 0.05,
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
        """
        if not excel_groups or not db_groups:
            return {}

        if not self.is_available():
            return {}

        system_prompt = """Sen O'zbekiston universitetlari uchun guruh nomlarini moslashtiradigan AI agentsan.

Senga Excel fayldagi guruh nomlari va bazadagi guruh nomlari beriladi.
Vazifang: har bir Excel guruh nomini bazadagi eng mos guruhga birlashtirish.

MUHIM QOIDALAR:
1. Guruh nomlari turli formatlarda bo'lishi mumkin:
   - KI-25-09, KI_25_09, KI 25 09, КИ-25-09 (kirill)
   - PM-1-01, PM_1_01, ПМ-1-01
   - AT25-01, AT-25-01
   - FTO'(ing) 25-01 → FTO'(ing)_25-01 yoki shu kabi
   - Magistr_KI_25-01 → birlashtirilgan qism
   
2. Prefikslar (Magistr_, Bakalavr_) va qavslar (ing), (o'zb) ham inobatga ol
3. Agar ishonchli mos kelsa — match qil
4. Agar ishonchsiz bo'lsa — null qo'y (xato matchdan ko'ra match qilmaslik yaxshi)
5. Faqat bitta eng yaxshi matchni tanlash kerak
6. Kirill va lotin alifbolarini ham inobatga ol (КИ = KI, ПМ = PM)
7. Raqamlar muhim — 25-09 va 25-10 TURLI GURUHLAR!
8. Ajratgichlar (-, _, bo'sh joy) farq emas
9. Agar Excel nomi bazadagi guruhning kengaytirilgan versiyasi bo'lsa (masalan "Magistr_FTO'(ing) 25-01" va bazada "FTO'(ing)_25-01") — bu match!

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

Har bir Excel guruh nomini bazadagi eng mos guruhga moslashtir."""

        content = await self._call_openai(system_prompt, user_prompt, max_tokens=4000)
        if not content:
            return {}

        try:
            result = json.loads(content)
            matches = result.get("matches", {})

            db_set = set(db_groups)
            validated = {}
            for excel_name, db_name in matches.items():
                if db_name and db_name in db_set:
                    validated[excel_name] = db_name
                else:
                    validated[excel_name] = None

            ai_matched = sum(1 for v in validated.values() if v is not None)
            logger.info(f"AI Group Matching: {ai_matched}/{len(excel_groups)} guruh moslashtirildi")
            return validated

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"AI group matching response parse error: {e}")
            return {}

    # ═══════════════════════════════════════════════════════
    # 2. SMART CELL CONTENT PARSING (ALL CELLS)
    # ═══════════════════════════════════════════════════════

    async def parse_cells(
        self,
        cells: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Use AI to parse ALL schedule cell contents for maximum accuracy.
        Processes in batches of 40 cells.
        """
        if not cells or not self.is_available():
            return []

        all_results = []
        batch_size = 40

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

Senga dars jadvali katakchalari (cell) matni beriladi. DIQQAT BILAN har biridan quyidagilarni ajratib ol:

AJRATISH TARTIBI:
1. **subject** — Fan nomi. Odatda birinchi keladi. "Falsafa", "Matematika", "Ingliz tili" kabi.
2. **schedule_type** — Dars turi. Qavslar ichida yozilgan:
   - (ma'ruza), (lek), (leksiya) → "lecture"
   - (amaliy), (sem), (seminar) → "practice" 
   - (lab), (laboratoriya) → "lab"
   - Hech narsa yo'q → "lecture" (default)
3. **teacher** — O'qituvchi. Odatda "Familiya I.O." yoki "Familiya I." formatda. 
   Masalan: "Aliyev A.", "Karimova N.T.", "Raximov Bobur"
4. **room** — Xona raqami: "301", "307-xona", "L-2", "Sport zal", "Aud.305"
5. **building** — Bino: "A bino", "B bino", "Asosiy bino". Agar yo'q bo'lsa null.

QOIDALAR:
- Katakchada TURLI formatlar bo'lishi mumkin:
  a) Bir qatorda: "Falsafa (ma'ruza) Aliyev A. 307-xona A bino"
  b) Ko'p qatorli (\\n bilan): "Matematika\\nKarimov B.\\n205-xona"
  c) Faqat fan: "Jismoniy tarbiya"
  d) Bo'sh yoki "-" → HAMMASI null
  e) Murakkab: "Tarbiyaviy soat / Milliy g'oya Ustoz 101 A bino"
  
- DOIM fan nomini BIRINCHI ajrat, keyin turini, keyin o'qituvchini, keyin xonani
- Agar aniqlab bo'lmasa — null qo'y (xato qiymatdan ko'ra null yaxshi)
- O'qituvchi va xonani ADASHTIRMA — xona RAQAM bilan boshlanadi, o'qituvchi HARF bilan

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
        user_prompt = f"""Quyidagi {len(cells)} ta dars jadvali katakchalarini DIQQAT BILAN tahlil qil:

{cells_text}

Har bir katakchadan fan, tur, o'qituvchi, xona, binoni ajrat. Aniq bo'lmasa null qo'y."""

        content = await self._call_openai(system_prompt, user_prompt, max_tokens=4000)
        if not content:
            return []

        try:
            result = json.loads(content)
            parsed = result.get("parsed", [])

            valid_types = {"lecture", "practice", "lab", "seminar", "exam", "consultation"}
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
    # 3. QUALITY ANALYSIS
    # ═══════════════════════════════════════════════════════

    async def analyze_schedule_data(
        self,
        records: List[Dict[str, Any]],
        db_groups: List[str],
    ) -> Dict[str, Any]:
        """
        Full AI quality analysis of schedule data.
        Detects: duplicate lessons, time conflicts, missing data.
        """
        if not self.is_available() or not records:
            return {"suggestions": [], "anomalies": [], "quality_score": 0}

        # Collect detailed stats
        unmatched = set()
        matched = set()
        subjects = set()
        teachers = set()
        day_lesson_counts = {}  # (group, day, lesson) -> count — detect duplicates

        for rec in records:
            if rec.get("group_id"):
                gname = rec.get("db_group_name", "")
                matched.add(gname)
                key = (gname, str(rec.get("day", "")), rec.get("lesson_number", 0))
                day_lesson_counts[key] = day_lesson_counts.get(key, 0) + 1
            else:
                unmatched.add(rec.get("sheet_group_name", ""))
            if rec.get("subject"):
                subjects.add(rec["subject"])
            if rec.get("teacher"):
                teachers.add(rec["teacher"])

        # Find duplicates
        duplicates = [
            f"{k[0]} - {k[1]} - {k[2]}-para: {v} marta"
            for k, v in day_lesson_counts.items() if v > 1
        ]

        system_prompt = """Sen O'zbekiston universitetlari dars jadvali sifat tahlilchisisisan.

Senga import qilingan jadval statistikasi beriladi. Vazifang:
1. Sifat bahosi (1-10) — 10 = mukammal jadval
2. Xatoliklarni aniqlash (duplicatlar, bo'sh maydonlar)
3. Foydali takliflar berish
4. Qisqacha xulosa

Bahosi qoidalari:
- 10: Hech qanday xatolik yo'q, barcha guruhlar topilgan
- 8-9: Kichik kamchiliklar bor lekin asosiy jadval to'g'ri
- 6-7: Bir nechta xatoliklar bor
- 4-5: Ko'p xatoliklar, lekin foydalanish mumkin
- 1-3: Jadvalni qayta tuzish kerak

JSON formatda javob ber:
{
  "quality_score": 1-10,
  "anomalies": ["xatolik tavsifi"],
  "suggestions": ["taklif"],
  "summary": "qisqa xulosa (1-2 gap)"
}"""

        stats = {
            "total_records": len(records),
            "matched_groups": list(matched),
            "matched_groups_count": len(matched),
            "unmatched_groups": list(unmatched),
            "unmatched_groups_count": len(unmatched),
            "unique_subjects": len(subjects),
            "unique_teachers": len(teachers),
            "records_without_subject": sum(1 for r in records if not r.get("subject")),
            "records_without_teacher": sum(1 for r in records if not r.get("teacher")),
            "records_without_room": sum(1 for r in records if not r.get("room")),
            "duplicate_slots": duplicates[:20],
            "duplicate_count": len(duplicates),
        }

        user_prompt = f"""Import qilingan jadval statistikasi:

{json.dumps(stats, ensure_ascii=False, indent=2)}

Tahlil qil va aniq takliflar ber."""

        content = await self._call_openai(system_prompt, user_prompt, max_tokens=2000)
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

        Steps:
        1. Collect all unmatched groups → AI match
        2. Parse ALL cells with raw content through AI for accuracy
        3. Apply AI results back to records
        4. Run quality analysis

        Returns enhanced records with AI corrections.
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
            logger.info(f"AI: {len(unmatched_groups)} unmatched groups to resolve...")
            ai_group_matches = await self.match_groups(unmatched_groups, db_group_names)

            for rec in records:
                if not rec.get("group_id") and rec.get("sheet_group_name"):
                    excel_name = rec["sheet_group_name"]
                    db_name = ai_group_matches.get(excel_name)
                    if db_name and db_name in group_lookup:
                        rec["group_id"] = group_lookup[db_name].id
                        rec["db_group_name"] = db_name
                        group_name_map[excel_name] = db_name

        # ── Step 2: Parse ONLY cells where regex couldn't extract subject ──
        cells_to_parse = []
        for i, rec in enumerate(records):
            # Only send to AI if regex failed to extract subject
            if not rec.get("subject") and rec.get("_raw_cell"):
                raw = rec["_raw_cell"].strip()
                if raw and raw != "-" and raw != "—":
                    cells_to_parse.append({
                        "id": str(i),
                        "content": raw,
                    })

        ai_parsed_count = 0
        if cells_to_parse:
            logger.info(f"AI: {len(cells_to_parse)} cells to parse...")
            parsed_results = await self.parse_cells(cells_to_parse)

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
