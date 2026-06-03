from __future__ import annotations

import json


SECTION_CATALOG = [
    {
        "code": "blood_bank",
        "name_ar": "زمرة وتصالب",
        "section_type": "panel",
        "items": [
            {
                "test_code": "abo_group",
                "label_ar": "الزمرة",
                "result_type": "choice",
                "default_choices": ["A", "B", "AB", "O"],
            },
            {
                "test_code": "rh_factor",
                "label_ar": "عامل Rh",
                "result_type": "choice",
                "default_choices": ["إيجابي", "سلبي"],
            },
            {
                "test_code": "crossmatch_result",
                "label_ar": "نتيجة التصالب",
                "result_type": "choice",
                "default_choices": ["متوافق", "غير متوافق"],
            },
            {
                "test_code": "blood_product",
                "label_ar": "نوع المنتج",
                "result_type": "choice",
                "default_choices": ["دم كامل", "كريات حمراء مكثفة", "بلازما"],
            },
        ],
    },
    {
        "code": "cbc",
        "name_ar": "CBC ثلاثي",
        "section_type": "panel",
        "items": [
            {"test_code": "wbc", "label_ar": "WBC", "result_type": "numeric", "default_unit_ar": "10^3/uL"},
            {"test_code": "rbc", "label_ar": "RBC", "result_type": "numeric", "default_unit_ar": "10^6/uL"},
            {"test_code": "hgb", "label_ar": "Hb", "result_type": "numeric", "default_unit_ar": "g/dL"},
            {"test_code": "hct", "label_ar": "HCT", "result_type": "numeric", "default_unit_ar": "%"},
            {"test_code": "plt", "label_ar": "PLT", "result_type": "numeric", "default_unit_ar": "10^3/uL"},
        ],
    },
    {
        "code": "electrolytes",
        "name_ar": "شوارد",
        "section_type": "panel",
        "items": [
            {"test_code": "sodium", "label_ar": "الصوديوم", "result_type": "numeric", "default_unit_ar": "mmol/L"},
            {"test_code": "potassium", "label_ar": "البوتاسيوم", "result_type": "numeric", "default_unit_ar": "mmol/L"},
            {"test_code": "chloride", "label_ar": "الكلور", "result_type": "numeric", "default_unit_ar": "mmol/L"},
        ],
    },
    {
        "code": "troponin",
        "name_ar": "تروبونين",
        "section_type": "panel",
        "items": [
            {
                "test_code": "troponin",
                "label_ar": "تروبونين",
                "result_type": "choice",
                "default_choices": ["إيجابي", "سلبي"],
            }
        ],
    },
    {
        "code": "viral_serology",
        "name_ar": "كبد B وC وHIV",
        "section_type": "panel",
        "items": [
            {
                "test_code": "hbsag",
                "label_ar": "HBsAg",
                "result_type": "choice",
                "default_choices": ["إيجابي", "سلبي"],
            },
            {
                "test_code": "hcv",
                "label_ar": "HCV",
                "result_type": "choice",
                "default_choices": ["إيجابي", "سلبي"],
            },
            {
                "test_code": "hiv",
                "label_ar": "HIV",
                "result_type": "choice",
                "default_choices": ["إيجابي", "سلبي"],
            },
        ],
    },
    {
        "code": "coagulation",
        "name_ar": "PT / PTT",
        "section_type": "panel",
        "items": [
            {"test_code": "pt", "label_ar": "PT", "result_type": "numeric", "default_unit_ar": "sec"},
            {"test_code": "ptt", "label_ar": "PTT", "result_type": "numeric", "default_unit_ar": "sec"},
        ],
    },
    {
        "code": "glucose",
        "name_ar": "سكر",
        "section_type": "panel",
        "items": [
            {"test_code": "glucose", "label_ar": "سكر الدم", "result_type": "numeric", "default_unit_ar": "mg/dL"}
        ],
    },
    {
        "code": "renal",
        "name_ar": "بولة / كرياتينين / حمض البول",
        "section_type": "panel",
        "items": [
            {"test_code": "urea", "label_ar": "بولة", "result_type": "numeric", "default_unit_ar": "mg/dL"},
            {"test_code": "creatinine", "label_ar": "كرياتينين", "result_type": "numeric", "default_unit_ar": "mg/dL"},
            {"test_code": "uric_acid", "label_ar": "حمض البول", "result_type": "numeric", "default_unit_ar": "mg/dL"},
        ],
    },
    {
        "code": "amylase",
        "name_ar": "أميلاز",
        "section_type": "panel",
        "items": [
            {"test_code": "amylase", "label_ar": "أميلاز", "result_type": "numeric", "default_unit_ar": "U/L"}
        ],
    },
    {
        "code": "inflammation",
        "name_ar": "CRP / سرعة تثفل",
        "section_type": "panel",
        "items": [
            {"test_code": "crp", "label_ar": "CRP", "result_type": "numeric", "default_unit_ar": "mg/L"},
            {"test_code": "esr", "label_ar": "سرعة التثفل", "result_type": "numeric", "default_unit_ar": "mm/hr"},
        ],
    },
    {
        "code": "liver",
        "name_ar": "ALT / AST / بيليروبين كلي ومباشر",
        "section_type": "panel",
        "items": [
            {"test_code": "alt", "label_ar": "ALT", "result_type": "numeric", "default_unit_ar": "U/L"},
            {"test_code": "ast", "label_ar": "AST", "result_type": "numeric", "default_unit_ar": "U/L"},
            {"test_code": "bilirubin_total", "label_ar": "بيليروبين كلي", "result_type": "numeric", "default_unit_ar": "mg/dL"},
            {"test_code": "bilirubin_direct", "label_ar": "بيليروبين مباشر", "result_type": "numeric", "default_unit_ar": "mg/dL"},
        ],
    },
    {
        "code": "proteins",
        "name_ar": "بروتين كلي / ألبومين",
        "section_type": "panel",
        "items": [
            {"test_code": "total_protein", "label_ar": "بروتين كلي", "result_type": "numeric", "default_unit_ar": "g/dL"},
            {"test_code": "albumin", "label_ar": "ألبومين", "result_type": "numeric", "default_unit_ar": "g/dL"},
        ],
    },
    {
        "code": "lipids",
        "name_ar": "شحوم / كوليسترول",
        "section_type": "panel",
        "items": [
            {"test_code": "triglycerides", "label_ar": "شحوم ثلاثية", "result_type": "numeric", "default_unit_ar": "mg/dL"},
            {"test_code": "cholesterol", "label_ar": "كوليسترول", "result_type": "numeric", "default_unit_ar": "mg/dL"},
        ],
    },
    {
        "code": "urine",
        "name_ar": "بول وراسب",
        "section_type": "structured",
        "items": [
            {"test_code": "urine_color", "label_ar": "اللون", "result_type": "text"},
            {"test_code": "urine_appearance", "label_ar": "المظهر", "result_type": "text"},
            {"test_code": "urine_ph", "label_ar": "التفاعل", "result_type": "text"},
            {"test_code": "urine_protein", "label_ar": "بروتين", "result_type": "choice", "default_choices": ["سلبي", "+", "++", "+++"]},
            {"test_code": "urine_glucose", "label_ar": "سكر", "result_type": "choice", "default_choices": ["سلبي", "+", "++", "+++"]},
            {"test_code": "urine_wbc", "label_ar": "كريات بيض", "result_type": "text"},
            {"test_code": "urine_rbc", "label_ar": "كريات حمر", "result_type": "text"},
            {"test_code": "urine_notes", "label_ar": "ملاحظات", "result_type": "text"},
        ],
    },
    {
        "code": "stool",
        "name_ar": "براز",
        "section_type": "structured",
        "items": [
            {"test_code": "stool_color", "label_ar": "اللون", "result_type": "text"},
            {"test_code": "stool_consistency", "label_ar": "القوام", "result_type": "text"},
            {"test_code": "stool_mucus", "label_ar": "مخاط", "result_type": "choice", "default_choices": ["سلبي", "إيجابي"]},
            {"test_code": "stool_blood", "label_ar": "دم", "result_type": "choice", "default_choices": ["سلبي", "إيجابي"]},
            {"test_code": "stool_ova", "label_ar": "بيض طفيليات", "result_type": "text"},
            {"test_code": "stool_notes", "label_ar": "ملاحظات", "result_type": "text"},
        ],
    },
    {
        "code": "csf",
        "name_ar": "CSF",
        "section_type": "structured",
        "items": [
            {"test_code": "csf_glucose", "label_ar": "سكر CSF", "result_type": "numeric", "default_unit_ar": "mg/dL"},
            {"test_code": "csf_protein", "label_ar": "بروتين CSF", "result_type": "numeric", "default_unit_ar": "mg/dL"},
            {"test_code": "csf_cell_count", "label_ar": "عد الخلايا", "result_type": "numeric", "default_unit_ar": "cells/uL"},
        ],
    },
    {
        "code": "agglutination",
        "name_ar": "فيدال / رايت",
        "section_type": "panel",
        "items": [
            {
                "test_code": "widal",
                "label_ar": "فيدال",
                "result_type": "choice",
                "default_choices": ["إيجابي", "سلبي"],
            },
            {
                "test_code": "wright",
                "label_ar": "رايت",
                "result_type": "choice",
                "default_choices": ["إيجابي", "سلبي"],
            },
        ],
    },
    {
        "code": "blood_smear",
        "name_ar": "لطاخة دموية",
        "section_type": "structured",
        "items": [
            {"test_code": "blood_smear_result", "label_ar": "وصف اللطاخة", "result_type": "text"}
        ],
    },
    {
        "code": "custom",
        "name_ar": "تقرير مخصص",
        "section_type": "custom",
        "items": [
            {"test_code": "custom_report_body", "label_ar": "تفاصيل التقرير", "result_type": "text"}
        ],
    },
]


REFERENCE_RANGES = [
    {"test_code": "wbc", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 4.0, "high_value": 11.0, "reference_text_ar": "4.0 - 11.0"},
    {"test_code": "rbc", "sex": "male", "min_age_days": None, "max_age_days": None, "low_value": 4.5, "high_value": 5.9, "reference_text_ar": "4.5 - 5.9"},
    {"test_code": "rbc", "sex": "female", "min_age_days": None, "max_age_days": None, "low_value": 4.1, "high_value": 5.1, "reference_text_ar": "4.1 - 5.1"},
    {"test_code": "hgb", "sex": "male", "min_age_days": None, "max_age_days": None, "low_value": 13.0, "high_value": 17.0, "reference_text_ar": "13.0 - 17.0"},
    {"test_code": "hgb", "sex": "female", "min_age_days": None, "max_age_days": None, "low_value": 12.0, "high_value": 15.0, "reference_text_ar": "12.0 - 15.0"},
    {"test_code": "hct", "sex": "male", "min_age_days": None, "max_age_days": None, "low_value": 40.0, "high_value": 52.0, "reference_text_ar": "40 - 52"},
    {"test_code": "hct", "sex": "female", "min_age_days": None, "max_age_days": None, "low_value": 36.0, "high_value": 48.0, "reference_text_ar": "36 - 48"},
    {"test_code": "plt", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 150.0, "high_value": 450.0, "reference_text_ar": "150 - 450"},
    {"test_code": "sodium", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 135.0, "high_value": 145.0, "reference_text_ar": "135 - 145"},
    {"test_code": "potassium", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 3.5, "high_value": 5.1, "reference_text_ar": "3.5 - 5.1"},
    {"test_code": "chloride", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 98.0, "high_value": 107.0, "reference_text_ar": "98 - 107"},
    {"test_code": "pt", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 11.0, "high_value": 13.5, "reference_text_ar": "11 - 13.5"},
    {"test_code": "ptt", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 25.0, "high_value": 35.0, "reference_text_ar": "25 - 35"},
    {"test_code": "glucose", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 70.0, "high_value": 110.0, "reference_text_ar": "70 - 110"},
    {"test_code": "urea", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 15.0, "high_value": 45.0, "reference_text_ar": "15 - 45"},
    {"test_code": "creatinine", "sex": "male", "min_age_days": 6570, "max_age_days": None, "low_value": 0.7, "high_value": 1.3, "reference_text_ar": "0.7 - 1.3"},
    {"test_code": "creatinine", "sex": "female", "min_age_days": 6570, "max_age_days": None, "low_value": 0.6, "high_value": 1.1, "reference_text_ar": "0.6 - 1.1"},
    {"test_code": "uric_acid", "sex": "male", "min_age_days": 6570, "max_age_days": None, "low_value": 3.4, "high_value": 7.0, "reference_text_ar": "3.4 - 7.0"},
    {"test_code": "uric_acid", "sex": "female", "min_age_days": 6570, "max_age_days": None, "low_value": 2.4, "high_value": 6.0, "reference_text_ar": "2.4 - 6.0"},
    {"test_code": "amylase", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 30.0, "high_value": 110.0, "reference_text_ar": "30 - 110"},
    {"test_code": "crp", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 0.0, "high_value": 5.0, "reference_text_ar": "0 - 5"},
    {"test_code": "esr", "sex": "male", "min_age_days": None, "max_age_days": None, "low_value": 0.0, "high_value": 15.0, "reference_text_ar": "0 - 15"},
    {"test_code": "esr", "sex": "female", "min_age_days": None, "max_age_days": None, "low_value": 0.0, "high_value": 20.0, "reference_text_ar": "0 - 20"},
    {"test_code": "alt", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 0.0, "high_value": 41.0, "reference_text_ar": "0 - 41"},
    {"test_code": "ast", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 0.0, "high_value": 40.0, "reference_text_ar": "0 - 40"},
    {"test_code": "bilirubin_total", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 0.2, "high_value": 1.2, "reference_text_ar": "0.2 - 1.2"},
    {"test_code": "bilirubin_direct", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 0.0, "high_value": 0.3, "reference_text_ar": "0 - 0.3"},
    {"test_code": "total_protein", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 6.0, "high_value": 8.3, "reference_text_ar": "6.0 - 8.3"},
    {"test_code": "albumin", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 3.5, "high_value": 5.2, "reference_text_ar": "3.5 - 5.2"},
    {"test_code": "triglycerides", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 0.0, "high_value": 150.0, "reference_text_ar": "حتى 150"},
    {"test_code": "cholesterol", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 0.0, "high_value": 200.0, "reference_text_ar": "حتى 200"},
    {"test_code": "csf_glucose", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 40.0, "high_value": 70.0, "reference_text_ar": "40 - 70"},
    {"test_code": "csf_protein", "sex": None, "min_age_days": None, "max_age_days": None, "low_value": 15.0, "high_value": 45.0, "reference_text_ar": "15 - 45"},
]


def iter_seed_rows():
    for section in SECTION_CATALOG:
        for index, item in enumerate(section["items"], start=1):
            yield {
                "section_code": section["code"],
                "test_code": item["test_code"],
                "label_ar": item["label_ar"],
                "result_type": item["result_type"],
                "default_unit_ar": item.get("default_unit_ar"),
                "default_choices_json": json.dumps(item.get("default_choices", []), ensure_ascii=False),
                "display_order": index,
                "is_active": 1,
            }


def iter_section_rows():
    for index, section in enumerate(SECTION_CATALOG, start=1):
        yield {
            "code": section["code"],
            "name_ar": section["name_ar"],
            "section_type": section["section_type"],
            "display_order": index,
            "is_active": 1,
        }


def get_section(section_code: str):
    for section in SECTION_CATALOG:
        if section["code"] == section_code:
            return section
    return None
