from __future__ import annotations

import json
import secrets
from datetime import date, datetime

from flask import render_template


SEX_LABELS = {
    "male": "ذكر",
    "female": "أنثى",
    "unknown": "غير محدد",
    None: "غير محدد",
}


FLAG_LABELS = {
    "H": "مرتفع",
    "L": "منخفض",
}

SECTION_TYPE_INFO = {
    "panel": {"label": "جدولي", "description": "قسم تحاليل قياسي يعرض النتائج ضمن جدول مختصر ومنظم."},
    "structured": {"label": "منظم", "description": "قسم وصفي منظم لتحاليل مثل البول أو البراز أو اللطاخة مع حقول متنوعة."},
    "custom": {"label": "حر", "description": "قسم نصي حر للتقارير الخاصة أو الحالات غير المعتادة."},
}


def generate_identifier(kind: str) -> str:
    prefix = {"patient": "PT", "report": "RP"}[kind]
    stamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    token = secrets.token_hex(3).upper()
    return f"{prefix}-{stamp}-{token}"


def parse_iso_date(value: str | None):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def build_iso_dob(form) -> str | None:
    day = (form.get("dob_day") or "").strip()
    month = (form.get("dob_month") or "").strip()
    year = (form.get("dob_year") or "").strip()
    if not any([day, month, year]):
        return None
    if not all([day, month, year]):
        raise ValueError("يجب اختيار اليوم والشهر والسنة بالكامل.")
    try:
        dob = date(int(year), int(month), int(day))
    except (TypeError, ValueError):
        raise ValueError("تاريخ الميلاد غير صالح.")
    return dob.isoformat()


def compute_patient_age_days(patient, report_date: str | None = None):
    if patient is None:
        return None

    report_day = parse_iso_date(report_date or date.today().isoformat())
    dob = parse_iso_date(patient["date_of_birth"])
    if dob:
        return max((report_day - dob).days, 0)

    age_value = patient["age_value"]
    age_unit = patient["age_unit"]
    if age_value in (None, "") or not age_unit:
        return None
    factor = {"days": 1, "months": 30, "years": 365}.get(age_unit)
    return int(age_value) * factor if factor else None


def format_age_from_days(age_days: int | None) -> str:
    if age_days is None:
        return "غير متاح"
    if age_days < 31:
        return f"{age_days} يوم"
    if age_days < 365:
        months = max(age_days // 30, 1)
        return f"{months} شهر"
    years = age_days // 365
    remainder_months = (age_days % 365) // 30
    if remainder_months:
        return f"{years} سنة و{remainder_months} شهر"
    return f"{years} سنة"


def age_summary(patient, report_date: str | None = None) -> str:
    return format_age_from_days(compute_patient_age_days(patient, report_date))


def get_lab_profile(db):
    row = db.execute("SELECT * FROM lab_profile WHERE id = 1").fetchone()
    return row


def update_lab_profile(db, form, logo_filename: str | None = None):
    profile = get_lab_profile(db)
    values = {
        "facility_name": (form.get("facility_name") or profile["facility_name"]).strip(),
        "report_title": (form.get("report_title") or profile["report_title"]).strip(),
        "report_subtitle": (form.get("report_subtitle") or profile["report_subtitle"] or "").strip() or None,
        "authority_line_1": (form.get("authority_line_1") or profile["authority_line_1"] or "").strip() or None,
        "authority_line_2": (form.get("authority_line_2") or profile["authority_line_2"] or "").strip() or None,
        "authority_line_3": (form.get("authority_line_3") or profile["authority_line_3"] or "").strip() or None,
        "header_notes": (form.get("header_notes") or profile["header_notes"] or "").strip() or None,
        "footer_text": (form.get("footer_text") or profile["footer_text"] or "").strip() or None,
        "logo_filename": profile["logo_filename"] if logo_filename is None else (logo_filename or None),
        "accent_color": (form.get("accent_color") or profile["accent_color"] or "").strip() or "#0f8f83",
    }
    db.execute(
        """
        UPDATE lab_profile
        SET facility_name = ?, report_title = ?, report_subtitle = ?, authority_line_1 = ?, authority_line_2 = ?, authority_line_3 = ?, header_notes = ?, footer_text = ?, logo_filename = ?, accent_color = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
        """,
        (
            values["facility_name"],
            values["report_title"],
            values["report_subtitle"],
            values["authority_line_1"],
            values["authority_line_2"],
            values["authority_line_3"],
            values["header_notes"],
            values["footer_text"],
            values["logo_filename"],
            values["accent_color"],
        ),
    )
    db.commit()


def get_catalog(db):
    rows = db.execute(
        """
        SELECT code, name_ar, section_type
        FROM section_templates
        WHERE is_active = 1
        ORDER BY display_order, code
        """
    ).fetchall()
    return [dict(row) for row in rows]


def get_section_choices(db):
    rows = db.execute(
        """
        SELECT code, name_ar
        FROM section_templates
        ORDER BY display_order, code
        """
    ).fetchall()
    return [dict(row) for row in rows]


def get_section_template(db, section_code: str):
    return db.execute(
        "SELECT * FROM section_templates WHERE code = ?",
        (section_code,),
    ).fetchone()


def get_section_definitions(db, section_code: str):
    rows = db.execute(
        """
        SELECT *
        FROM test_definitions
        WHERE section_code = ? AND is_active = 1
        ORDER BY display_order, id
        """,
        (section_code,),
    ).fetchall()
    definitions = []
    for row in rows:
        item = dict(row)
        item["choices"] = json.loads(item["default_choices_json"] or "[]")
        definitions.append(item)
    return definitions


def build_definition_map(db):
    rows = db.execute("SELECT * FROM test_definitions").fetchall()
    mapping = {}
    for row in rows:
        item = dict(row)
        item["choices"] = json.loads(item["default_choices_json"] or "[]")
        mapping[item["test_code"]] = item
    return mapping


def _parse_optional_float(value, field_label: str):
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError(f"{field_label} يجب أن يكون رقماً صالحاً.") from exc


def get_default_reference_range(db, test_code: str):
    return db.execute(
        """
        SELECT *
        FROM reference_ranges
        WHERE test_code = ? AND sex IS NULL AND min_age_days IS NULL AND max_age_days IS NULL
        ORDER BY id DESC
        LIMIT 1
        """,
        (test_code,),
    ).fetchone()


def get_specific_reference_ranges(db, test_code: str):
    rows = db.execute(
        """
        SELECT *
        FROM reference_ranges
        WHERE test_code = ?
          AND NOT (sex IS NULL AND min_age_days IS NULL AND max_age_days IS NULL)
        ORDER BY
            CASE WHEN sex IS NULL THEN 1 ELSE 0 END,
            COALESCE(min_age_days, 0),
            COALESCE(max_age_days, 999999)
        """,
        (test_code,),
    ).fetchall()
    return [dict(row) for row in rows]


def upsert_default_reference_range(db, test_code: str, low_value, high_value, reference_text_ar: str | None):
    existing = get_default_reference_range(db, test_code)
    has_value = low_value is not None or high_value is not None or reference_text_ar
    if not has_value:
        if existing is not None:
            db.execute("DELETE FROM reference_ranges WHERE id = ?", (existing["id"],))
        return
    if existing is None:
        db.execute(
            """
            INSERT INTO reference_ranges
            (test_code, sex, min_age_days, max_age_days, low_value, high_value, reference_text_ar)
            VALUES (?, NULL, NULL, NULL, ?, ?, ?)
            """,
            (test_code, low_value, high_value, reference_text_ar),
        )
    else:
        db.execute(
            """
            UPDATE reference_ranges
            SET low_value = ?, high_value = ?, reference_text_ar = ?
            WHERE id = ?
            """,
            (low_value, high_value, reference_text_ar, existing["id"]),
        )


def _parse_optional_int(value, field_label: str):
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{field_label} يجب أن يكون رقماً صحيحاً.") from exc


def _age_value_to_days(value, unit, field_label: str):
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        amount = int(raw)
    except ValueError as exc:
        raise ValueError(f"{field_label} يجب أن يكون رقماً صحيحاً.") from exc
    unit = (unit or "").strip() or "days"
    factors = {"days": 1, "months": 30, "years": 365}
    if unit not in factors:
        raise ValueError("وحدة العمر المرجعي غير صالحة.")
    return amount * factors[unit]


def _days_to_age_parts(days):
    if days in (None, ""):
        return {"value": "", "unit": "days"}
    days = int(days)
    if days % 365 == 0 and days >= 365:
        return {"value": str(days // 365), "unit": "years"}
    if days % 30 == 0 and days >= 30:
        return {"value": str(days // 30), "unit": "months"}
    return {"value": str(days), "unit": "days"}


def create_specific_reference_range(db, test_code: str, form):
    sex = (form.get("sex") or "").strip() or None
    min_age_days = _age_value_to_days(form.get("min_age_value") or form.get("min_age_days"), form.get("min_age_unit"), "العمر الأدنى")
    max_age_days = _age_value_to_days(form.get("max_age_value") or form.get("max_age_days"), form.get("max_age_unit"), "العمر الأعلى")
    low_value = _parse_optional_float(form.get("low_value"), "الحد الأدنى")
    high_value = _parse_optional_float(form.get("high_value"), "الحد الأعلى")
    reference_text = (form.get("reference_text_ar") or "").strip() or None

    if sex not in {None, "male", "female"}:
        raise ValueError("قيمة الجنس المرجعي غير صالحة.")
    if min_age_days is not None and max_age_days is not None and min_age_days > max_age_days:
        raise ValueError("العمر الأدنى لا يمكن أن يكون أكبر من العمر الأعلى.")
    if all(value is None for value in (low_value, high_value, reference_text)):
        raise ValueError("أدخل قيمة مرجعية واحدة على الأقل أو مرجعاً مطبوعاً.")

    db.execute(
        """
        INSERT INTO reference_ranges
        (test_code, sex, min_age_days, max_age_days, low_value, high_value, reference_text_ar)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (test_code, sex, min_age_days, max_age_days, low_value, high_value, reference_text),
    )
    db.commit()


def update_specific_reference_range(db, range_id: int, test_code: str, form):
    current = db.execute(
        """
        SELECT *
        FROM reference_ranges
        WHERE id = ? AND test_code = ?
        """,
        (range_id, test_code),
    ).fetchone()
    if current is None:
        raise ValueError("القاعدة المرجعية غير موجودة.")

    sex = (form.get("sex") or "").strip() or None
    min_age_days = _age_value_to_days(form.get("min_age_value") or form.get("min_age_days"), form.get("min_age_unit"), "العمر الأدنى")
    max_age_days = _age_value_to_days(form.get("max_age_value") or form.get("max_age_days"), form.get("max_age_unit"), "العمر الأعلى")
    low_value = _parse_optional_float(form.get("low_value"), "الحد الأدنى")
    high_value = _parse_optional_float(form.get("high_value"), "الحد الأعلى")
    reference_text = (form.get("reference_text_ar") or "").strip() or None

    if sex not in {None, "male", "female"}:
        raise ValueError("قيمة الجنس المرجعي غير صالحة.")
    if min_age_days is not None and max_age_days is not None and min_age_days > max_age_days:
        raise ValueError("العمر الأدنى لا يمكن أن يكون أكبر من العمر الأعلى.")
    if all(value is None for value in (low_value, high_value, reference_text)):
        raise ValueError("أدخل قيمة مرجعية واحدة على الأقل أو مرجعاً مطبوعاً.")

    db.execute(
        """
        UPDATE reference_ranges
        SET sex = ?, min_age_days = ?, max_age_days = ?, low_value = ?, high_value = ?, reference_text_ar = ?
        WHERE id = ? AND test_code = ?
        """,
        (sex, min_age_days, max_age_days, low_value, high_value, reference_text, range_id, test_code),
    )
    db.commit()


def delete_specific_reference_range(db, range_id: int, test_code: str):
    current = db.execute(
        """
        SELECT *
        FROM reference_ranges
        WHERE id = ? AND test_code = ?
        """,
        (range_id, test_code),
    ).fetchone()
    if current is None:
        raise ValueError("القاعدة المرجعية غير موجودة.")
    db.execute("DELETE FROM reference_ranges WHERE id = ? AND test_code = ?", (range_id, test_code))
    db.commit()


def get_template_overview(db):
    sections = db.execute(
        """
        SELECT *
        FROM section_templates
        ORDER BY display_order, code
        """
    ).fetchall()
    tests = db.execute(
        """
        SELECT *
        FROM test_definitions
        ORDER BY section_code, display_order, id
        """
    ).fetchall()
    grouped = {}
    for test in tests:
        row = dict(test)
        row["choices"] = json.loads(row["default_choices_json"] or "[]")
        default_range = get_default_reference_range(db, row["test_code"])
        row["default_range"] = dict(default_range) if default_range is not None else None
        specific_ranges = get_specific_reference_ranges(db, row["test_code"])
        for range_row in specific_ranges:
            range_row["min_age_parts"] = _days_to_age_parts(range_row["min_age_days"])
            range_row["max_age_parts"] = _days_to_age_parts(range_row["max_age_days"])
        row["specific_ranges"] = specific_ranges
        grouped.setdefault(test["section_code"], []).append(row)
    overview = []
    for section in sections:
        item = dict(section)
        item["tests"] = grouped.get(section["code"], [])
        item["active_test_count"] = sum(1 for test in item["tests"] if test["is_active"])
        overview.append(item)
    return overview


def create_section_template(db, form):
    code = (form.get("code") or "").strip().lower().replace(" ", "_")
    name_ar = (form.get("name_ar") or "").strip()
    section_type = (form.get("section_type") or "").strip()
    if not code or not name_ar or section_type not in {"panel", "structured", "custom"}:
        raise ValueError("بيانات القسم الجديد غير مكتملة.")
    exists = db.execute("SELECT 1 FROM section_templates WHERE code = ?", (code,)).fetchone()
    if exists is not None:
        raise ValueError("رمز القسم مستخدم مسبقاً.")
    next_order = db.execute(
        "SELECT COALESCE(MAX(display_order), 0) + 1 AS next_order FROM section_templates"
    ).fetchone()["next_order"]
    db.execute(
        """
        INSERT INTO section_templates (code, name_ar, section_type, display_order, is_active)
        VALUES (?, ?, ?, ?, 1)
        """,
        (code, name_ar, section_type, next_order),
    )
    db.commit()


def create_test_definition(db, form):
    section_code = (form.get("section_code") or "").strip()
    test_code = (form.get("test_code") or "").strip().lower().replace(" ", "_")
    label_ar = (form.get("label_ar") or "").strip()
    result_type = (form.get("result_type") or "").strip()
    default_unit_ar = (form.get("default_unit_ar") or "").strip() or None
    choices_text = (form.get("default_choices") or "").strip()
    reference_text = (form.get("reference_text_ar") or "").strip() or None
    low_value = _parse_optional_float(form.get("low_value"), "الحد الأدنى")
    high_value = _parse_optional_float(form.get("high_value"), "الحد الأعلى")
    if not section_code or not test_code or not label_ar or result_type not in {"numeric", "choice", "text"}:
        raise ValueError("بيانات التحليل الجديد غير مكتملة.")
    section = db.execute("SELECT 1 FROM section_templates WHERE code = ?", (section_code,)).fetchone()
    if section is None:
        raise ValueError("القسم المحدد غير موجود.")
    exists = db.execute("SELECT 1 FROM test_definitions WHERE test_code = ?", (test_code,)).fetchone()
    if exists is not None:
        raise ValueError("رمز التحليل مستخدم مسبقاً.")
    next_order = db.execute(
        "SELECT COALESCE(MAX(display_order), 0) + 1 AS next_order FROM test_definitions WHERE section_code = ?",
        (section_code,),
    ).fetchone()["next_order"]
    choices = [choice.strip() for choice in choices_text.split(",") if choice.strip()] if result_type == "choice" else []
    if result_type != "numeric":
        default_unit_ar = None
        low_value = None
        high_value = None
        reference_text = None
    db.execute(
        """
        INSERT INTO test_definitions
        (section_code, test_code, label_ar, result_type, default_unit_ar, default_choices_json, display_order, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """,
        (
            section_code,
            test_code,
            label_ar,
            result_type,
            default_unit_ar,
            json.dumps(choices, ensure_ascii=False),
            next_order,
        ),
    )
    if result_type == "numeric":
        upsert_default_reference_range(db, test_code, low_value, high_value, reference_text)
    db.commit()


def get_patient_reports(db, patient_id: int, limit: int | None = None):
    sql = """
        SELECT *
        FROM reports
        WHERE patient_id = ?
        ORDER BY report_date DESC, id DESC
    """
    params = [patient_id]
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)
    return db.execute(
        sql,
        params,
    ).fetchall()


def get_dashboard_summary(db):
    return db.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM reports WHERE report_date = DATE('now', 'localtime')) AS reports_today,
            (SELECT COUNT(*) FROM reports WHERE status = 'draft') AS draft_reports,
            (SELECT COUNT(*) FROM patients) AS patient_count
        """
    ).fetchone()


def update_section_template(db, section_code: str, form):
    name_ar = (form.get("name_ar") or "").strip()
    is_active = 1 if form.get("is_active") == "on" else 0
    if not name_ar:
        raise ValueError("اسم القسم مطلوب.")
    db.execute(
        "UPDATE section_templates SET name_ar = ?, is_active = ? WHERE code = ?",
        (name_ar, is_active, section_code),
    )
    db.commit()


def delete_section_template(db, section_code: str):
    section = db.execute("SELECT * FROM section_templates WHERE code = ?", (section_code,)).fetchone()
    if section is None:
        raise ValueError("القسم غير موجود.")
    tests = db.execute("SELECT test_code FROM test_definitions WHERE section_code = ?", (section_code,)).fetchall()
    for test in tests:
        db.execute("DELETE FROM reference_ranges WHERE test_code = ?", (test["test_code"],))
    db.execute("DELETE FROM test_definitions WHERE section_code = ?", (section_code,))
    db.execute("DELETE FROM section_templates WHERE code = ?", (section_code,))
    db.commit()


def update_test_definition(db, test_id: int, form):
    current = db.execute("SELECT * FROM test_definitions WHERE id = ?", (test_id,)).fetchone()
    if current is None:
        raise ValueError("التحليل غير موجود.")
    label_ar = (form.get("label_ar") or "").strip()
    result_type = (form.get("result_type") or "").strip()
    default_unit_ar = (form.get("default_unit_ar") or "").strip() or None
    choices_text = (form.get("default_choices") or "").strip()
    reference_text = (form.get("reference_text_ar") or "").strip() or None
    low_value = _parse_optional_float(form.get("low_value"), "الحد الأدنى")
    high_value = _parse_optional_float(form.get("high_value"), "الحد الأعلى")
    is_active = 1 if form.get("is_active") == "on" else 0
    if not label_ar:
        raise ValueError("اسم التحليل مطلوب.")
    if result_type not in {"numeric", "choice", "text"}:
        raise ValueError("نوع الحقل غير صالح.")
    choices = [choice.strip() for choice in choices_text.split(",") if choice.strip()] if result_type == "choice" else []
    if result_type != "numeric":
        default_unit_ar = None
        low_value = None
        high_value = None
        reference_text = None
    db.execute(
        """
        UPDATE test_definitions
        SET label_ar = ?, result_type = ?, default_unit_ar = ?, default_choices_json = ?, is_active = ?
        WHERE id = ?
        """,
        (
            label_ar,
            result_type,
            default_unit_ar,
            json.dumps(choices, ensure_ascii=False),
            is_active,
            test_id,
        ),
    )
    upsert_default_reference_range(db, current["test_code"], low_value, high_value, reference_text)
    db.commit()


def delete_test_definition(db, test_id: int):
    current = db.execute("SELECT * FROM test_definitions WHERE id = ?", (test_id,)).fetchone()
    if current is None:
        raise ValueError("التحليل غير موجود.")
    db.execute("DELETE FROM reference_ranges WHERE test_code = ?", (current["test_code"],))
    db.execute("DELETE FROM test_definitions WHERE id = ?", (test_id,))
    db.commit()


def create_patient(db, form):
    full_name = (form.get("full_name") or "").strip()
    sex = form.get("sex") or "unknown"
    date_of_birth = build_iso_dob(form)

    if not full_name:
        raise ValueError("اسم المريض مطلوب.")
    if not date_of_birth:
        raise ValueError("تاريخ الميلاد مطلوب.")

    patient_number = generate_identifier("patient")
    db.execute(
        """
        INSERT INTO patients
        (patient_number, full_name, sex, date_of_birth, phone, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            patient_number,
            full_name,
            sex,
            date_of_birth,
            (form.get("phone") or "").strip() or None,
            (form.get("notes") or "").strip() or None,
        ),
    )
    db.commit()
    return db.execute("SELECT * FROM patients WHERE patient_number = ?", (patient_number,)).fetchone()


def create_report(db, patient_id: int, form):
    patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    if patient is None:
        raise ValueError("المريض غير موجود.")

    profile = get_lab_profile(db)
    report_number = generate_identifier("report")
    report_date = form.get("report_date") or date.today().isoformat()
    db.execute(
        """
        INSERT INTO reports
        (report_number, patient_id, report_date, lab_header_text, lab_footer_text, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            report_number,
            patient_id,
            report_date,
            profile["facility_name"],
            profile["footer_text"],
            (form.get("notes") or "").strip() or None,
        ),
    )
    db.commit()
    return db.execute("SELECT * FROM reports WHERE report_number = ?", (report_number,)).fetchone()


def get_patient(db, patient_id: int):
    return db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()


def get_report(db, report_id: int):
    return db.execute(
        """
        SELECT reports.*, patients.full_name AS patient_name
        FROM reports
        JOIN patients ON patients.id = reports.patient_id
        WHERE reports.id = ?
        """,
        (report_id,),
    ).fetchone()


def get_recent_reports(db, limit: int = 5):
    return db.execute(
        """
        SELECT reports.id, reports.report_number, reports.report_date, reports.status, reports.print_count,
               patients.full_name AS patient_name
        FROM reports
        JOIN patients ON patients.id = reports.patient_id
        ORDER BY reports.created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def search_patients(db, query: str | None, page: int = 1, per_page: int = 5):
    page = max(page, 1)
    offset = (page - 1) * per_page
    if not query:
        return [], 0

    like_query = f"%{query.strip()}%"
    total = db.execute(
        """
        SELECT COUNT(*) AS count
        FROM patients
        WHERE full_name LIKE ?
        """,
        (like_query,),
    ).fetchone()["count"]
    rows = db.execute(
        """
        SELECT *
        FROM patients
        WHERE full_name LIKE ?
        ORDER BY updated_at DESC, id DESC
        LIMIT ? OFFSET ?
        """,
        (like_query, per_page, offset),
    ).fetchall()
    return rows, total


def get_history(db, query: str | None, report_date: str | None, page: int = 1, per_page: int = 10):
    sql = """
        SELECT reports.*, patients.full_name AS patient_name
        FROM reports
        JOIN patients ON patients.id = reports.patient_id
        WHERE 1 = 1
    """
    count_sql = """
        SELECT COUNT(*) AS count
        FROM reports
        JOIN patients ON patients.id = reports.patient_id
        WHERE 1 = 1
    """
    params = []
    count_params = []
    searched = bool((query or "").strip() or report_date)
    if query:
        sql += " AND (patients.full_name LIKE ? OR reports.report_number LIKE ?)"
        count_sql += " AND (patients.full_name LIKE ? OR reports.report_number LIKE ?)"
        like_query = f"%{query.strip()}%"
        params.extend([like_query, like_query])
        count_params.extend([like_query, like_query])
    if report_date:
        sql += " AND reports.report_date = ?"
        count_sql += " AND reports.report_date = ?"
        params.append(report_date)
        count_params.append(report_date)
    sql += " ORDER BY reports.report_date DESC, reports.id DESC"
    if not searched:
        sql += " LIMIT 10"
        rows = db.execute(sql, params).fetchall()
        return rows, len(rows)
    total = db.execute(count_sql, count_params).fetchone()["count"]
    page = max(page, 1)
    offset = (page - 1) * per_page
    sql += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])
    rows = db.execute(sql, params).fetchall()
    return rows, total


def get_existing_section_codes(db, report_id: int):
    rows = db.execute(
        "SELECT section_code FROM report_sections WHERE report_id = ?",
        (report_id,),
    ).fetchall()
    return {row["section_code"] for row in rows}


def add_section_to_report(db, report_id: int, section_code: str, custom_name: str | None = None):
    report = get_report(db, report_id)
    if report is None:
        raise ValueError("التقرير غير موجود.")
    if report["status"] != "draft":
        raise ValueError("لا يمكن تعديل تقرير نهائي.")

    section = get_section_template(db, section_code)
    if section is None:
        raise ValueError("القسم المطلوب غير موجود.")
    if section["is_active"] != 1:
        raise ValueError("هذا القسم غير مفعل حالياً.")

    existing_codes = get_existing_section_codes(db, report_id)
    if section_code != "custom" and section_code in existing_codes:
        raise ValueError("تمت إضافة هذا القسم مسبقاً.")

    next_order = db.execute(
        "SELECT COALESCE(MAX(display_order), 0) + 1 AS next_order FROM report_sections WHERE report_id = ?",
        (report_id,),
    ).fetchone()["next_order"]

    section_name = (custom_name or "").strip() if section_code == "custom" else section["name_ar"]
    if not section_name:
        section_name = section["name_ar"]

    cursor = db.execute(
        """
        INSERT INTO report_sections
        (report_id, section_code, section_name_ar, section_type, display_order)
        VALUES (?, ?, ?, ?, ?)
        """,
        (report_id, section_code, section_name, section["section_type"], next_order),
    )
    section_id = cursor.lastrowid

    definitions = get_section_definitions(db, section_code)
    for definition in definitions:
        db.execute(
            """
            INSERT INTO report_items
            (report_section_id, test_code, label_ar, result_type, unit_ar, display_order)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                section_id,
                definition["test_code"],
                definition["label_ar"],
                definition["result_type"],
                definition["default_unit_ar"],
                definition["display_order"],
            ),
        )

    db.commit()
    return section_id


def delete_section(db, report_id: int, section_id: int):
    report = get_report(db, report_id)
    if report is None or report["status"] != "draft":
        raise ValueError("لا يمكن حذف قسم من تقرير نهائي.")
    db.execute("DELETE FROM report_sections WHERE id = ? AND report_id = ?", (section_id, report_id))
    db.commit()


def cancel_draft_report(db, report_id: int):
    report = get_report(db, report_id)
    if report is None:
        raise ValueError("التقرير غير موجود.")
    if report["status"] != "draft":
        raise ValueError("يمكن إلغاء المسودات فقط.")
    db.execute("DELETE FROM reports WHERE id = ? AND status = 'draft'", (report_id,))
    db.commit()


def get_reference_range(db, test_code: str, sex: str | None, age_days: int | None):
    rows = db.execute(
        """
        SELECT *
        FROM reference_ranges
        WHERE test_code = ?
          AND (sex = ? OR sex IS NULL)
        ORDER BY CASE WHEN sex IS NULL THEN 1 ELSE 0 END,
                 COALESCE(min_age_days, 0) DESC
        """,
        (test_code, sex),
    ).fetchall()

    for row in rows:
        if row["min_age_days"] is not None and age_days is not None and age_days < row["min_age_days"]:
            continue
        if row["max_age_days"] is not None and age_days is not None and age_days > row["max_age_days"]:
            continue
        if age_days is None and (row["min_age_days"] is not None or row["max_age_days"] is not None):
            continue
        return row
    return None


def calculate_flag(value_numeric, reference_range):
    if value_numeric is None or reference_range is None:
        return None
    if reference_range["low_value"] is not None and value_numeric < reference_range["low_value"]:
        return "L"
    if reference_range["high_value"] is not None and value_numeric > reference_range["high_value"]:
        return "H"
    return None


def update_report(db, report_id: int, form):
    report = get_report(db, report_id)
    if report is None:
        raise ValueError("التقرير غير موجود.")
    if report["status"] != "draft":
        raise ValueError("لا يمكن تعديل تقرير نهائي.")

    patient = get_patient(db, report["patient_id"])
    next_report_date = form.get("report_date") or report["report_date"]
    age_days = compute_patient_age_days(patient, next_report_date)

    db.execute(
        """
        UPDATE reports
        SET report_date = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (
            next_report_date,
            (form.get("notes") or "").strip() or None,
            report_id,
        ),
    )

    items = db.execute(
        """
        SELECT report_items.*
        FROM report_items
        JOIN report_sections ON report_sections.id = report_items.report_section_id
        WHERE report_sections.report_id = ?
        ORDER BY report_sections.display_order, report_items.display_order
        """,
        (report_id,),
    ).fetchall()

    for item in items:
        value_text = None
        value_numeric = None
        value_choice = None

        if item["result_type"] == "numeric":
            raw_value = (form.get(f"item-{item['id']}-numeric") or "").strip()
            if raw_value:
                try:
                    value_numeric = float(raw_value)
                except ValueError as exc:
                    raise ValueError(f"القيمة الرقمية غير صالحة في {item['label_ar']}.") from exc
        elif item["result_type"] == "choice":
            value_choice = (form.get(f"item-{item['id']}-choice") or "").strip() or None
        else:
            value_text = (form.get(f"item-{item['id']}-text") or "").strip() or None

        reference_override = (form.get(f"item-{item['id']}-reference") or "").strip()
        reference_range = get_reference_range(db, item["test_code"], patient["sex"], age_days)
        reference_text = reference_override or (reference_range["reference_text_ar"] if reference_range else None)
        flag = calculate_flag(value_numeric, reference_range)

        db.execute(
            """
            UPDATE report_items
            SET value_text = ?, value_numeric = ?, value_choice = ?, unit_ar = ?, reference_text_ar = ?, flag = ?, comment = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (
                value_text,
                value_numeric,
                value_choice,
                (form.get(f"item-{item['id']}-unit") or item["unit_ar"] or "").strip() or None,
                reference_text,
                flag,
                (form.get(f"item-{item['id']}-comment") or "").strip() or None,
                item["id"],
            ),
        )

    db.commit()


def enrich_item_display(db, patient, report_date: str, item: dict):
    age_days = compute_patient_age_days(patient, report_date)
    reference_range = get_reference_range(db, item["test_code"], patient["sex"], age_days)
    item["reference_display"] = item["reference_text_ar"] or (reference_range["reference_text_ar"] if reference_range else "")
    item["computed_flag"] = item["flag"] or calculate_flag(item["value_numeric"], reference_range)
    item["flag_label"] = FLAG_LABELS.get(item["computed_flag"], "")
    item["flag_class"] = {
        "H": "is-high",
        "L": "is-low",
    }.get(item["computed_flag"], "")
    if item["result_type"] == "numeric":
        item["display_value"] = "" if item["value_numeric"] is None else f"{item['value_numeric']:g}"
    elif item["result_type"] == "choice":
        item["display_value"] = item["value_choice"] or ""
    else:
        item["display_value"] = item["value_text"] or ""
    return item


def get_report_bundle(db, report_id: int):
    report = db.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if report is None:
        return None

    patient = get_patient(db, report["patient_id"])
    profile = get_lab_profile(db)
    sections = db.execute(
        """
        SELECT *
        FROM report_sections
        WHERE report_id = ?
        ORDER BY display_order, id
        """,
        (report_id,),
    ).fetchall()

    items = db.execute(
        """
        SELECT report_items.*
        FROM report_items
        JOIN report_sections ON report_sections.id = report_items.report_section_id
        WHERE report_sections.report_id = ?
        ORDER BY report_sections.display_order, report_items.display_order, report_items.id
        """,
        (report_id,),
    ).fetchall()

    definitions = build_definition_map(db)
    section_items = {}
    for item in items:
        data = dict(item)
        definition = definitions.get(item["test_code"], {})
        data["choices"] = definition.get("choices", [])
        data = enrich_item_display(db, patient, report["report_date"], data)
        section_items.setdefault(item["report_section_id"], []).append(data)

    bundle_sections = []
    for section in sections:
        section_data = dict(section)
        section_data["items"] = section_items.get(section["id"], [])
        bundle_sections.append(section_data)

    return {
        "report": report,
        "patient": patient,
        "profile": profile,
        "sections": bundle_sections,
        "patient_age_days": compute_patient_age_days(patient, report["report_date"]),
        "patient_age_display": age_summary(patient, report["report_date"]),
    }


def render_snapshot_html(bundle):
    return render_template(
        "reports/_print_document.html",
        report=bundle["report"],
        patient=bundle["patient"],
        profile=bundle["profile"],
        sections=bundle["sections"],
        patient_age_days=bundle["patient_age_days"],
        patient_age_display=bundle["patient_age_display"],
        sex_labels=SEX_LABELS,
    )


def finalize_report(db, report_id: int):
    bundle = get_report_bundle(db, report_id)
    if bundle is None:
        raise ValueError("التقرير غير موجود.")
    if bundle["report"]["status"] != "draft":
        raise ValueError("التقرير منجز مسبقاً.")

    snapshot_html = render_snapshot_html(bundle)
    db.execute(
        """
        UPDATE reports
        SET status = 'final', finalized_at = CURRENT_TIMESTAMP, snapshot_html = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (snapshot_html, report_id),
    )
    db.commit()


def record_print(db, report_id: int):
    db.execute(
        """
        UPDATE reports
        SET print_count = print_count + 1, printed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (report_id,),
    )
    db.commit()


def create_revision(db, report_id: int):
    bundle = get_report_bundle(db, report_id)
    if bundle is None:
        raise ValueError("التقرير غير موجود.")
    if bundle["report"]["status"] != "final":
        raise ValueError("يمكن إنشاء نسخة مراجعة فقط من تقرير نهائي.")

    new_report_number = generate_identifier("report")
    cursor = db.execute(
        """
        INSERT INTO reports
        (report_number, patient_id, report_date, status, revision_of_report_id, lab_header_text, lab_footer_text, notes)
        VALUES (?, ?, ?, 'draft', ?, ?, ?, ?)
        """,
        (
            new_report_number,
            bundle["report"]["patient_id"],
            bundle["report"]["report_date"],
            report_id,
            bundle["report"]["lab_header_text"],
            bundle["report"]["lab_footer_text"],
            bundle["report"]["notes"],
        ),
    )
    new_report_id = cursor.lastrowid

    for section in bundle["sections"]:
        new_section = db.execute(
            """
            INSERT INTO report_sections
            (report_id, section_code, section_name_ar, section_type, display_order)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                new_report_id,
                section["section_code"],
                section["section_name_ar"],
                section["section_type"],
                section["display_order"],
            ),
        )

        for item in section["items"]:
            db.execute(
                """
                INSERT INTO report_items
                (report_section_id, test_code, label_ar, result_type, value_text, value_numeric, value_choice, unit_ar, reference_text_ar, flag, comment, display_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_section.lastrowid,
                    item["test_code"],
                    item["label_ar"],
                    item["result_type"],
                    item["value_text"],
                    item["value_numeric"],
                    item["value_choice"],
                    item["unit_ar"],
                    item["reference_text_ar"],
                    item["computed_flag"],
                    item["comment"],
                    item["display_order"],
                ),
            )

    db.commit()
    return new_report_id
