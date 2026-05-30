import re
from datetime import date
from typing import Any

EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def _parse_float(value: Any, field_name: str) -> tuple[float | None, str | None]:
  if value is None or (isinstance(value, str) and not value.strip()):
    return None, f"{field_name} is required."
  try:
    number = float(value)
  except (TypeError, ValueError):
    return None, f"{field_name} must be a valid number."
  if number < 0:
    return None, f"{field_name} must be zero or greater."
  return number, None


def validate_patient_form(data: dict) -> tuple[dict | None, list[str]]:
  errors: list[str] = []
  cleaned: dict = {}

  full_name = (data.get("full_name") or "").strip()
  if not full_name:
    errors.append("Full name is required.")
  elif len(full_name) > 120:
    errors.append("Full name must be 120 characters or fewer.")
  else:
    cleaned["full_name"] = full_name

  dob_raw = (data.get("date_of_birth") or "").strip()
  if not dob_raw:
    errors.append("Date of birth is required.")
  else:
    try:
      dob = date.fromisoformat(dob_raw)
      if dob > date.today():
        errors.append("Date of birth cannot be in the future.")
      else:
        cleaned["date_of_birth"] = dob
    except ValueError:
      errors.append("Date of birth must be a valid date (YYYY-MM-DD).")

  email = (data.get("email") or "").strip()
  if not email:
    errors.append("Email address is required.")
  elif not EMAIL_PATTERN.match(email):
    errors.append("Please enter a valid email address.")
  elif len(email) > 120:
    errors.append("Email must be 120 characters or fewer.")
  else:
    cleaned["email"] = email.lower()

  for field, label in (
    ("glucose", "Glucose"),
    ("haemoglobin", "Haemoglobin"),
    ("cholesterol", "Cholesterol"),
  ):
    value, err = _parse_float(data.get(field), label)
    if err:
      errors.append(err)
    else:
      cleaned[field] = value

  return (cleaned if not errors else None), errors
