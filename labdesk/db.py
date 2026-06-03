from __future__ import annotations

import sqlite3

from flask import current_app, g

from .seeds import REFERENCE_RANGES, iter_section_rows, iter_seed_rows


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_number TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    sex TEXT,
    date_of_birth TEXT,
    age_value INTEGER,
    age_unit TEXT,
    phone TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_number TEXT NOT NULL UNIQUE,
    patient_id INTEGER NOT NULL,
    report_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    revision_of_report_id INTEGER,
    finalized_at TEXT,
    printed_at TEXT,
    print_count INTEGER NOT NULL DEFAULT 0,
    lab_header_text TEXT,
    lab_footer_text TEXT,
    snapshot_html TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients (id),
    FOREIGN KEY (revision_of_report_id) REFERENCES reports (id),
    CHECK (status IN ('draft', 'final'))
);

CREATE TABLE IF NOT EXISTS report_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    section_code TEXT NOT NULL,
    section_name_ar TEXT NOT NULL,
    section_type TEXT NOT NULL,
    display_order INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS report_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_section_id INTEGER NOT NULL,
    test_code TEXT NOT NULL,
    label_ar TEXT NOT NULL,
    result_type TEXT NOT NULL,
    value_text TEXT,
    value_numeric REAL,
    value_choice TEXT,
    unit_ar TEXT,
    reference_text_ar TEXT,
    flag TEXT,
    comment TEXT,
    display_order INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_section_id) REFERENCES report_sections (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS section_templates (
    code TEXT PRIMARY KEY,
    name_ar TEXT NOT NULL,
    section_type TEXT NOT NULL,
    display_order INTEGER NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS test_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_code TEXT NOT NULL,
    test_code TEXT NOT NULL UNIQUE,
    label_ar TEXT NOT NULL,
    result_type TEXT NOT NULL,
    default_unit_ar TEXT,
    default_choices_json TEXT,
    display_order INTEGER NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (section_code) REFERENCES section_templates (code)
);

CREATE TABLE IF NOT EXISTS reference_ranges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_code TEXT NOT NULL,
    sex TEXT,
    min_age_days INTEGER,
    max_age_days INTEGER,
    low_value REAL,
    high_value REAL,
    reference_text_ar TEXT
);

CREATE TABLE IF NOT EXISTS lab_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    facility_name TEXT NOT NULL,
    report_title TEXT NOT NULL,
    report_subtitle TEXT,
    authority_line_1 TEXT,
    authority_line_2 TEXT,
    authority_line_3 TEXT,
    header_notes TEXT,
    footer_text TEXT,
    logo_filename TEXT,
    accent_color TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


DEFAULT_PROFILE = {
    "id": 1,
    "facility_name": "المخبر الطبي",
    "report_title": "نتائج التحاليل المخبرية",
    "report_subtitle": "Laboratory Results",
    "authority_line_1": "",
    "authority_line_2": "",
    "authority_line_3": "",
    "header_notes": "",
    "footer_text": "اسم الفني: __________    التوقيع: __________    الختم: __________",
    "logo_filename": None,
    "accent_color": "#0f8f83",
}


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _table_columns(db: sqlite3.Connection, table_name: str) -> set[str]:
    rows = db.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row["name"] for row in rows}


def run_migrations(db: sqlite3.Connection) -> None:
    patient_columns = _table_columns(db, "patients")
    if "date_of_birth" not in patient_columns:
        db.execute("ALTER TABLE patients ADD COLUMN date_of_birth TEXT")
    if "age_value" not in patient_columns:
        db.execute("ALTER TABLE patients ADD COLUMN age_value INTEGER")
    if "age_unit" not in patient_columns:
        db.execute("ALTER TABLE patients ADD COLUMN age_unit TEXT")

    report_columns = _table_columns(db, "reports")
    if "lab_header_text" not in report_columns:
        db.execute("ALTER TABLE reports ADD COLUMN lab_header_text TEXT")
    if "lab_footer_text" not in report_columns:
        db.execute("ALTER TABLE reports ADD COLUMN lab_footer_text TEXT")
    if "snapshot_html" not in report_columns:
        db.execute("ALTER TABLE reports ADD COLUMN snapshot_html TEXT")

    test_columns = _table_columns(db, "test_definitions")
    if "default_choices_json" not in test_columns:
        db.execute("ALTER TABLE test_definitions ADD COLUMN default_choices_json TEXT")
    if "is_active" not in test_columns:
        db.execute("ALTER TABLE test_definitions ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")

    profile_columns = _table_columns(db, "lab_profile")
    if "authority_line_1" not in profile_columns:
        db.execute("ALTER TABLE lab_profile ADD COLUMN authority_line_1 TEXT")
    if "authority_line_2" not in profile_columns:
        db.execute("ALTER TABLE lab_profile ADD COLUMN authority_line_2 TEXT")
    if "authority_line_3" not in profile_columns:
        db.execute("ALTER TABLE lab_profile ADD COLUMN authority_line_3 TEXT")
    if "accent_color" not in profile_columns:
        db.execute("ALTER TABLE lab_profile ADD COLUMN accent_color TEXT")


def init_db() -> None:
    db = get_db()
    db.executescript(SCHEMA)
    run_migrations(db)
    seed_db(db)
    db.commit()


def seed_db(db: sqlite3.Connection) -> None:
    section_count = db.execute("SELECT COUNT(*) AS count FROM section_templates").fetchone()["count"]
    if section_count == 0:
        db.executemany(
            """
            INSERT INTO section_templates
            (code, name_ar, section_type, display_order, is_active)
            VALUES
            (:code, :name_ar, :section_type, :display_order, :is_active)
            """,
            list(iter_section_rows()),
        )

    test_count = db.execute("SELECT COUNT(*) AS count FROM test_definitions").fetchone()["count"]
    if test_count == 0:
        db.executemany(
            """
            INSERT INTO test_definitions
            (section_code, test_code, label_ar, result_type, default_unit_ar, default_choices_json, display_order, is_active)
            VALUES
            (:section_code, :test_code, :label_ar, :result_type, :default_unit_ar, :default_choices_json, :display_order, :is_active)
            """,
            list(iter_seed_rows()),
        )

    range_count = db.execute("SELECT COUNT(*) AS count FROM reference_ranges").fetchone()["count"]
    if range_count == 0:
        db.executemany(
            """
            INSERT INTO reference_ranges
            (test_code, sex, min_age_days, max_age_days, low_value, high_value, reference_text_ar)
            VALUES
            (:test_code, :sex, :min_age_days, :max_age_days, :low_value, :high_value, :reference_text_ar)
            """,
            REFERENCE_RANGES,
        )

    profile_exists = db.execute("SELECT 1 FROM lab_profile WHERE id = 1").fetchone()
    if profile_exists is None:
        db.execute(
            """
            INSERT INTO lab_profile
            (id, facility_name, report_title, report_subtitle, authority_line_1, authority_line_2, authority_line_3, header_notes, footer_text, logo_filename, accent_color)
            VALUES
            (:id, :facility_name, :report_title, :report_subtitle, :authority_line_1, :authority_line_2, :authority_line_3, :header_notes, :footer_text, :logo_filename, :accent_color)
            """,
            DEFAULT_PROFILE,
        )
    else:
        db.execute(
            """
            UPDATE lab_profile
            SET accent_color = COALESCE(accent_color, ?),
                authority_line_1 = COALESCE(authority_line_1, ?),
                authority_line_2 = COALESCE(authority_line_2, ?),
                authority_line_3 = COALESCE(authority_line_3, ?),
                header_notes = COALESCE(header_notes, ?)
            WHERE id = 1
            """,
            (
                DEFAULT_PROFILE["accent_color"],
                DEFAULT_PROFILE["authority_line_1"],
                DEFAULT_PROFILE["authority_line_2"],
                DEFAULT_PROFILE["authority_line_3"],
                DEFAULT_PROFILE["header_notes"],
            ),
        )


def init_app(app) -> None:
    @app.cli.command("init-db")
    def init_db_command():
        init_db()
        print("Initialized the database.")
