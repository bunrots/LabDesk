from __future__ import annotations

import os
import secrets
from datetime import date

from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from .db import get_db
from .services import (
    SEX_LABELS,
    add_section_to_report,
    cancel_draft_report,
    age_summary,
    create_section_template,
    create_patient,
    create_report,
    create_revision,
    create_test_definition,
    delete_section,
    finalize_report,
    get_catalog,
    get_dashboard_summary,
    get_history,
    get_lab_profile,
    get_patient,
    get_patient_reports,
    get_recent_reports,
    get_report_bundle,
    get_section_choices,
    get_template_overview,
    record_print,
    render_snapshot_html,
    search_patients,
    update_lab_profile,
    update_report,
    update_section_template,
    update_test_definition,
)


bp = Blueprint("app", __name__)


def _dob_context():
    current_year = date.today().year
    return {
        "dob_days": [f"{day:02d}" for day in range(1, 32)],
        "dob_months": [(f"{month:02d}", label) for month, label in enumerate([
            "",
            "كانون الثاني",
            "شباط",
            "آذار",
            "نيسان",
            "أيار",
            "حزيران",
            "تموز",
            "آب",
            "أيلول",
            "تشرين الأول",
            "تشرين الثاني",
            "كانون الأول",
        ]) if month],
        "dob_years": [str(year) for year in range(current_year, current_year - 110, -1)],
    }


def _logo_upload_dir() -> str:
    path = os.path.join(current_app.instance_path, "uploads")
    os.makedirs(path, exist_ok=True)
    return path


def _save_logo(upload) -> str | None:
    if upload is None or not upload.filename:
        return None
    original_name = secure_filename(upload.filename)
    if not original_name:
        return None
    _, extension = os.path.splitext(original_name)
    filename = f"logo-{secrets.token_hex(8)}{extension.lower()}"
    upload.save(os.path.join(_logo_upload_dir(), filename))
    return filename


@bp.app_context_processor
def inject_site_profile():
    db = get_db()
    return {"site_profile": get_lab_profile(db)}


@bp.route("/assets/logo/<path:filename>")
def uploaded_logo(filename: str):
    path = os.path.join(_logo_upload_dir(), filename)
    if not os.path.exists(path):
        abort(404)
    return send_from_directory(_logo_upload_dir(), filename)


@bp.route("/", methods=["GET", "POST"])
@bp.route("/patients", methods=["GET", "POST"])
def patients_index():
    db = get_db()

    if request.method == "POST":
        try:
            patient = create_patient(db, request.form)
            report = create_report(db, patient["id"], {})
            flash("تم حفظ المريض بنجاح.", "success")
            return redirect(url_for("app.edit_report", report_id=report["id"]))
        except ValueError as exc:
            flash(str(exc), "error")

    query = request.args.get("q", "").strip()
    page = request.args.get("page", type=int) or 1
    patients, patient_total = search_patients(db, query, page=page, per_page=5)
    recent_reports = get_recent_reports(db, limit=5)
    summary = get_dashboard_summary(db)
    patient_cards = []
    for patient in patients:
        patient_cards.append(
            {
                "row": patient,
                "age_display": age_summary(patient),
            }
        )
    return render_template(
        "patients/index.html",
        patients=patient_cards,
        query=query,
        recent_reports=recent_reports,
        patient_total=patient_total,
        page=page,
        has_prev=page > 1,
        has_next=page * 5 < patient_total,
        summary=summary,
        today=date.today().isoformat(),
        sex_labels=SEX_LABELS,
        **_dob_context(),
    )


@bp.route("/patients/<int:patient_id>")
def patient_detail(patient_id: int):
    db = get_db()
    patient = get_patient(db, patient_id)
    if patient is None:
        flash("المريض غير موجود.", "error")
        return redirect(url_for("app.patients_index"))

    reports = get_patient_reports(db, patient_id)
    return render_template(
        "patients/show.html",
        patient=patient,
        reports=reports,
        patient_age_display=age_summary(patient),
        sex_labels=SEX_LABELS,
    )


@bp.route("/reports/new", methods=["GET", "POST"])
def new_report():
    db = get_db()
    patient_id = request.form.get("patient_id", type=int) or request.args.get("patient_id", type=int)
    if request.method != "POST":
        flash("أنشئ التقرير من شاشة المريض أو الاستقبال.", "error")
        return redirect(url_for("app.patients_index"))
    patient = get_patient(db, patient_id) if patient_id else None
    if patient is None:
        flash("اختر مريضاً قبل إنشاء التقرير.", "error")
        return redirect(url_for("app.patients_index"))

    try:
        report = create_report(db, patient_id, request.form)
        flash("تم إنشاء التقرير كمسودة.", "success")
        return redirect(url_for("app.edit_report", report_id=report["id"]))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("app.patient_detail", patient_id=patient_id))


@bp.route("/reports/<int:report_id>/edit", methods=["GET", "POST"])
def edit_report(report_id: int):
    db = get_db()
    bundle = get_report_bundle(db, report_id)
    if bundle is None:
        flash("التقرير غير موجود.", "error")
        return redirect(url_for("app.patients_index"))

    if bundle["report"]["status"] == "final":
        return redirect(url_for("app.show_report", report_id=report_id))

    if request.method == "POST":
        try:
            update_report(db, report_id, request.form)
            flash("تم حفظ نتائج التقرير.", "success")
            return redirect(url_for("app.edit_report", report_id=report_id))
        except ValueError as exc:
            flash(str(exc), "error")

    catalog = get_catalog(db)
    existing_codes = {section["section_code"] for section in bundle["sections"]}
    return render_template(
        "reports/edit.html",
        bundle=bundle,
        catalog=catalog,
        existing_codes=existing_codes,
        sex_labels=SEX_LABELS,
    )


@bp.post("/reports/<int:report_id>/sections")
def add_report_section(report_id: int):
    db = get_db()
    section_code = request.form.get("section_code") or ""
    custom_name = request.form.get("custom_name")
    try:
        add_section_to_report(db, report_id, section_code, custom_name)
        flash("تمت إضافة القسم إلى التقرير.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("app.edit_report", report_id=report_id))


@bp.post("/reports/<int:report_id>/sections/<int:section_id>/delete")
def delete_report_section(report_id: int, section_id: int):
    db = get_db()
    try:
        delete_section(db, report_id, section_id)
        flash("تم حذف القسم من المسودة.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("app.edit_report", report_id=report_id))


@bp.post("/reports/<int:report_id>/cancel")
def cancel_report_draft(report_id: int):
    db = get_db()
    try:
        cancel_draft_report(db, report_id)
        flash("تم إلغاء المسودة وحذفها.", "success")
        return redirect(url_for("app.patients_index"))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("app.edit_report", report_id=report_id))


@bp.route("/reports/<int:report_id>/preview")
def preview_report(report_id: int):
    db = get_db()
    bundle = get_report_bundle(db, report_id)
    if bundle is None:
        flash("التقرير غير موجود.", "error")
        return redirect(url_for("app.patients_index"))
    return render_template(
        "reports/preview.html",
        bundle=bundle,
        snapshot_html=None,
        sex_labels=SEX_LABELS,
    )


@bp.post("/reports/<int:report_id>/finalize")
def finalize_report_view(report_id: int):
    db = get_db()
    try:
        finalize_report(db, report_id)
        flash("تم اعتماد التقرير وأصبح جاهزاً للطباعة.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("app.edit_report", report_id=report_id))
    return redirect(url_for("app.show_report", report_id=report_id))


@bp.route("/reports/history")
def report_history():
    db = get_db()
    query = request.args.get("q", "").strip()
    report_date = request.args.get("report_date", "").strip() or None
    page = request.args.get("page", type=int) or 1
    rows, total = get_history(db, query, report_date, page=page, per_page=10)
    searched = bool(query or report_date)
    return render_template(
        "reports/history.html",
        reports=rows,
        query=query,
        report_date=report_date or "",
        page=page,
        total=total,
        searched=searched,
        has_prev=searched and page > 1,
        has_next=searched and page * 10 < total,
    )


@bp.route("/reports/<int:report_id>")
def show_report(report_id: int):
    db = get_db()
    bundle = get_report_bundle(db, report_id)
    if bundle is None:
        flash("التقرير غير موجود.", "error")
        return redirect(url_for("app.patients_index"))

    if bundle["report"]["status"] == "draft":
        return redirect(url_for("app.edit_report", report_id=report_id))

    snapshot_html = bundle["report"]["snapshot_html"]
    if current_app.debug or not snapshot_html:
        snapshot_html = render_snapshot_html(bundle)

    return render_template(
        "reports/show.html",
        bundle=bundle,
        snapshot_html=snapshot_html,
    )


@bp.post("/reports/<int:report_id>/print-log")
def report_print_log(report_id: int):
    db = get_db()
    record_print(db, report_id)
    return jsonify({"ok": True})


@bp.post("/reports/<int:report_id>/revise")
def revise_report(report_id: int):
    db = get_db()
    try:
        new_report_id = create_revision(db, report_id)
        flash("تم إنشاء نسخة مراجعة جديدة.", "success")
        return redirect(url_for("app.edit_report", report_id=new_report_id))
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("app.show_report", report_id=report_id))


@bp.route("/settings", methods=["GET", "POST"])
def settings():
    db = get_db()
    profile = get_lab_profile(db)
    if request.method == "POST":
        logo_filename = None
        if request.form.get("remove_logo") == "on":
            logo_filename = ""
        elif "logo_file" in request.files:
            logo_filename = _save_logo(request.files["logo_file"])
        try:
            update_lab_profile(db, request.form, logo_filename if logo_filename is not None else None)
            flash("تم تحديث إعدادات المخبر.", "success")
            return redirect(url_for("app.settings"))
        except ValueError as exc:
            flash(str(exc), "error")
            profile = get_lab_profile(db)

    templates = get_template_overview(db)
    return render_template(
        "settings/index.html",
        profile=profile,
        templates=templates,
        section_choices=get_section_choices(db),
        accent_presets=[
            "#0f8f83",
            "#155b9c",
            "#0f6f5a",
            "#6b7280",
            "#8a5b16",
        ],
    )


@bp.post("/settings/templates/sections")
def create_section_template_view():
    db = get_db()
    try:
        create_section_template(db, request.form)
        flash("تمت إضافة قسم جديد.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("app.settings"))


@bp.post("/settings/templates/tests")
def create_test_template_view():
    db = get_db()
    try:
        create_test_definition(db, request.form)
        flash("تمت إضافة تحليل جديد.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("app.settings"))


@bp.post("/settings/templates/sections/<section_code>")
def update_section_template_view(section_code: str):
    db = get_db()
    try:
        update_section_template(db, section_code, request.form)
        flash("تم تحديث القالب.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("app.settings"))


@bp.post("/settings/templates/tests/<int:test_id>")
def update_test_template_view(test_id: int):
    db = get_db()
    try:
        update_test_definition(db, test_id, request.form)
        flash("تم تحديث التحليل.", "success")
    except ValueError as exc:
        flash(str(exc), "error")
    return redirect(url_for("app.settings"))
