import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

load_dotenv()

from config import Config
from health_service import (
  generate_health_remarks,
  get_marker_assessments,
  parse_remarks,
  remarks_summary,
)
from models import Patient, db
from validators import validate_patient_form

BASE_DIR = Path(__file__).resolve().parent


def create_app(config_class: type = Config) -> Flask:
  app = Flask(__name__)
  app.config.from_object(config_class)

  instance_path = BASE_DIR / "instance"
  instance_path.mkdir(exist_ok=True)

  db.init_app(app)

  with app.app_context():
    db.create_all()

  @app.context_processor
  def inject_globals():
    from datetime import date

    return {
      "today": date.today().isoformat(),
      "parse_remarks": parse_remarks,
      "remarks_summary": remarks_summary,
    }

  register_routes(app)
  return app


def register_routes(app: Flask) -> None:
  @app.route("/")
  def index():
    patients = Patient.query.order_by(Patient.updated_at.desc()).all()
    return render_template("index.html", patients=patients)

  @app.route("/patients/new", methods=["GET", "POST"])
  def create_patient():
    if request.method == "GET":
      return render_template("patient_form.html", patient=None, action="create")

    cleaned, errors = validate_patient_form(request.form)
    if errors:
      for error in errors:
        flash(error, "danger")
      return render_template(
        "patient_form.html",
        patient=request.form.to_dict(),
        action="create",
      ), 400

    age = _age_from_dob(cleaned["date_of_birth"])
    remarks = generate_health_remarks(
      cleaned["glucose"],
      cleaned["haemoglobin"],
      cleaned["cholesterol"],
      age,
    )

    patient = Patient(
      full_name=cleaned["full_name"],
      date_of_birth=cleaned["date_of_birth"],
      email=cleaned["email"],
      glucose=cleaned["glucose"],
      haemoglobin=cleaned["haemoglobin"],
      cholesterol=cleaned["cholesterol"],
      remarks=remarks,
    )
    db.session.add(patient)
    db.session.commit()
    flash("Patient record created successfully.", "success")
    return redirect(url_for("view_patient", patient_id=patient.id))

  @app.route("/patients/<int:patient_id>")
  def view_patient(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    return render_template(
      "patient_detail.html",
      patient=patient,
      remarks_data=parse_remarks(patient.remarks or ""),
      lab_markers=get_marker_assessments(
        patient.glucose,
        patient.haemoglobin,
        patient.cholesterol,
      ),
    )

  @app.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
  def edit_patient(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)

    if request.method == "GET":
      return render_template("patient_form.html", patient=patient, action="edit")

    cleaned, errors = validate_patient_form(request.form)
    if errors:
      for error in errors:
        flash(error, "danger")
      return render_template(
        "patient_form.html",
        patient=request.form.to_dict(),
        action="edit",
      ), 400

    age = _age_from_dob(cleaned["date_of_birth"])
    remarks = generate_health_remarks(
      cleaned["glucose"],
      cleaned["haemoglobin"],
      cleaned["cholesterol"],
      age,
    )

    patient.full_name = cleaned["full_name"]
    patient.date_of_birth = cleaned["date_of_birth"]
    patient.email = cleaned["email"]
    patient.glucose = cleaned["glucose"]
    patient.haemoglobin = cleaned["haemoglobin"]
    patient.cholesterol = cleaned["cholesterol"]
    patient.remarks = remarks
    db.session.commit()
    flash("Patient record updated successfully.", "success")
    return redirect(url_for("view_patient", patient_id=patient.id))

  @app.route("/patients/<int:patient_id>/delete", methods=["POST"])
  def delete_patient(patient_id: int):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    flash("Patient record deleted.", "info")
    return redirect(url_for("index"))


def _age_from_dob(dob) -> int:
  from datetime import date

  today = date.today()
  years = today.year - dob.year
  if (today.month, today.day) < (dob.month, dob.day):
    years -= 1
  return years


app = create_app()

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(debug=True, host="0.0.0.0", port=port)
