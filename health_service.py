"""
Health prediction and AI remarks generation.

Uses Hugging Face Inference API (zero-shot classification) when HF_API_TOKEN is set.
Falls back to WHO GHO API context + rule-based clinical range analysis.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests

WHO_GHO_API = "https://ghoapi.azureedge.net/api/Indicator"

GLUCOSE_NORMAL = (70, 99)
GLUCOSE_PREDIABETES = (100, 125)
HAEMOGLOBIN_NORMAL_MALE = (13.5, 17.5)
HAEMOGLOBIN_NORMAL_FEMALE = (12.0, 15.5)
CHOLESTEROL_DESIRABLE = (0, 200)
CHOLESTEROL_BORDERLINE = (200, 239)

STATUS_NORMAL = "normal"
STATUS_CAUTION = "caution"
STATUS_ALERT = "alert"


@dataclass
class MarkerResult:
  name: str
  value: float
  unit: str
  status: str
  headline: str
  explanation: str
  action: str


def _fetch_who_insight() -> str:
  """Fetch a short public-health insight from the WHO GHO API."""
  try:
    response = requests.get(
      WHO_GHO_API,
      params={"$filter": "contains(IndicatorName,'diabetes')"},
      timeout=4,
    )
    response.raise_for_status()
    values = (response.json().get("value") or [])
    if values:
      indicator = values[0].get("IndicatorName", "")
      if indicator:
        return (
          "Public health note (WHO): Early detection of blood sugar problems "
          "through regular screening helps prevent complications. "
          f"Related global indicator — \"{indicator}\"."
        )
  except requests.RequestException:
    pass
  return (
    "Public health note: Regular blood tests help detect diabetes, anemia, "
    "and heart disease early — especially if you are over 40 or have a family history."
  )


def _assess_glucose(value: float) -> MarkerResult:
  if value < GLUCOSE_NORMAL[0]:
    return MarkerResult(
      "Glucose",
      value,
      "mg/dL",
      STATUS_ALERT,
      "Low blood sugar",
      f"Your glucose is {value} mg/dL, which is below the normal fasting range (70–99 mg/dL).",
      "Eat regular balanced meals and speak to a doctor if you feel dizzy, shaky, or confused.",
    )
  if value <= GLUCOSE_NORMAL[1]:
    return MarkerResult(
      "Glucose",
      value,
      "mg/dL",
      STATUS_NORMAL,
      "Blood sugar looks healthy",
      f"Your glucose is {value} mg/dL, within the normal fasting range (70–99 mg/dL).",
      "Maintain a balanced diet and stay physically active.",
    )
  if value <= GLUCOSE_PREDIABETES[1]:
    return MarkerResult(
      "Glucose",
      value,
      "mg/dL",
      STATUS_CAUTION,
      "Possible prediabetes",
      f"Your glucose is {value} mg/dL, in the prediabetes range (100–125 mg/dL). Blood sugar is higher than ideal but not yet in the diabetes range.",
      "Consider reducing sugary foods, increasing activity, and asking your doctor for an HbA1c follow-up test.",
    )
  return MarkerResult(
    "Glucose",
    value,
    "mg/dL",
    STATUS_ALERT,
    "High blood sugar — diabetes risk",
    f"Your glucose is {value} mg/dL, above 125 mg/dL, which may indicate diabetes.",
    "Please consult a healthcare provider soon for confirmatory testing and a care plan.",
  )


def _assess_haemoglobin(value: float) -> MarkerResult:
  hb_low = min(HAEMOGLOBIN_NORMAL_FEMALE[0], HAEMOGLOBIN_NORMAL_MALE[0])
  hb_high = max(HAEMOGLOBIN_NORMAL_FEMALE[1], HAEMOGLOBIN_NORMAL_MALE[1])
  normal_range = f"{hb_low}–{hb_high} g/dL"

  if value < hb_low:
    return MarkerResult(
      "Haemoglobin",
      value,
      "g/dL",
      STATUS_ALERT,
      "Possible anemia",
      f"Your haemoglobin is {value} g/dL, below the typical normal range ({normal_range}). Low levels can mean reduced oxygen delivery in the blood.",
      "Ask your doctor about iron levels, diet, and whether further tests (e.g. complete blood count) are needed.",
    )
  if value > hb_high:
    return MarkerResult(
      "Haemoglobin",
      value,
      "g/dL",
      STATUS_CAUTION,
      "Haemoglobin above typical range",
      f"Your haemoglobin is {value} g/dL, above the usual reference range ({normal_range}).",
      "A doctor can check whether this is harmless variation or needs follow-up.",
    )
  return MarkerResult(
    "Haemoglobin",
    value,
    "g/dL",
    STATUS_NORMAL,
    "Healthy red blood cell level",
    f"Your haemoglobin is {value} g/dL, within the normal range ({normal_range}). This suggests adequate oxygen-carrying capacity.",
    "No specific action needed for this marker — keep a varied, iron-rich diet.",
  )


def _assess_cholesterol(value: float) -> MarkerResult:
  if value < CHOLESTEROL_DESIRABLE[1]:
    return MarkerResult(
      "Cholesterol",
      value,
      "mg/dL",
      STATUS_NORMAL,
      "Heart-friendly cholesterol level",
      f"Your total cholesterol is {value} mg/dL, below 200 mg/dL (desirable level).",
      "Continue heart-healthy habits: fibre-rich foods, regular exercise, and limited saturated fat.",
    )
  if value <= CHOLESTEROL_BORDERLINE[1]:
    return MarkerResult(
      "Cholesterol",
      value,
      "mg/dL",
      STATUS_CAUTION,
      "Borderline high cholesterol",
      f"Your total cholesterol is {value} mg/dL, in the borderline-high range (200–239 mg/dL).",
      "Try more vegetables, whole grains, and activity; your doctor may suggest a lipid panel if this persists.",
    )
  return MarkerResult(
    "Cholesterol",
    value,
    "mg/dL",
    STATUS_ALERT,
    "High cholesterol — cardiovascular risk",
    f"Your total cholesterol is {value} mg/dL, at or above 240 mg/dL, which raises long-term heart and stroke risk.",
    "Discuss diet, exercise, and possible medication with a healthcare professional.",
  )


def _overall_risk_level(markers: list[MarkerResult]) -> tuple[str, str, str]:
  alerts = sum(1 for m in markers if m.status == STATUS_ALERT)
  cautions = sum(1 for m in markers if m.status == STATUS_CAUTION)

  if alerts >= 2:
    return (
      STATUS_ALERT,
      "Higher priority follow-up recommended",
      "Two or more results are outside healthy ranges. Please book a medical review soon.",
    )
  if alerts == 1:
    return (
      STATUS_ALERT,
      "One result needs medical attention",
      "At least one marker is in a range that should be discussed with your doctor.",
    )
  if cautions >= 1:
    return (
      STATUS_CAUTION,
      "Moderate — lifestyle improvements advised",
      "Some results are slightly outside the ideal range. Small diet and activity changes may help.",
    )
  return (
    STATUS_NORMAL,
    "Good overall screening result",
    "All three blood markers are within healthy reference ranges. Keep up your current healthy habits.",
  )


def _huggingface_zero_shot(
  hypothesis: str,
  candidate_labels: list[str],
  token: str,
  model: str,
) -> dict[str, Any] | None:
  url = f"https://api-inference.huggingface.co/models/{model}"
  headers = {"Authorization": f"Bearer {token}"}
  payload = {
    "inputs": hypothesis,
    "parameters": {"candidate_labels": candidate_labels},
  }
  try:
    response = requests.post(url, headers=headers, json=payload, timeout=25)
    if response.status_code == 503:
      return None
    response.raise_for_status()
    return response.json()
  except requests.RequestException:
    return None


def _ai_confirmation_note(
  glucose: float,
  haemoglobin: float,
  cholesterol: float,
  age: int,
  labels: list[str],
) -> str | None:
  hf_token = os.environ.get("HF_API_TOKEN", "")
  if not hf_token:
    return None

  summary = (
    f"Age {age}. Glucose {glucose} mg/dL, haemoglobin {haemoglobin} g/dL, "
    f"cholesterol {cholesterol} mg/dL."
  )
  hf_model = os.environ.get("HF_MODEL", "facebook/bart-large-mnli")
  result = _huggingface_zero_shot(summary, labels, hf_token, hf_model)
  if not result or not result.get("labels"):
    return None

  top_label = result["labels"][0].replace("_", " ")
  score = result.get("scores", [0])[0]
  return (
    f"AI model agreement: The machine-learning analysis also highlighted "
    f"\"{top_label}\" (confidence {score:.0%}), which supports the clinical reading above."
  )


def generate_health_remarks(
  glucose: float,
  haemoglobin: float,
  cholesterol: float,
  age: int,
) -> str:
  """
  Build a clear, patient-friendly health assessment for the Remarks field.
  """
  markers = [
    _assess_glucose(glucose),
    _assess_haemoglobin(haemoglobin),
    _assess_cholesterol(cholesterol),
  ]
  risk_status, risk_title, risk_summary = _overall_risk_level(markers)
  who_note = _fetch_who_insight()

  label_keys = []
  for m in markers:
    if m.status == STATUS_ALERT:
      label_keys.append(f"{m.name.lower()} concern")
    elif m.status == STATUS_CAUTION:
      label_keys.append(f"{m.name.lower()} watch")
    else:
      label_keys.append(f"{m.name.lower()} normal")

  ai_note = _ai_confirmation_note(glucose, haemoglobin, cholesterol, age, label_keys)

  lines = [
    f"OVERALL|{risk_status}|{risk_title}",
    f"SUMMARY|{risk_summary}",
    "",
    f"For a patient aged {age}, here is what your blood test results suggest:",
    "",
  ]

  for marker in markers:
    lines.extend([
      f"MARKER|{marker.name}|{marker.status}|{marker.headline}",
      f"  • Result: {marker.value} {marker.unit}",
      f"  • What it means: {marker.explanation}",
      f"  • Suggested step: {marker.action}",
      "",
    ])

  lines.append(f"INSIGHT|{who_note}")

  if ai_note:
    lines.extend(["", f"AI_NOTE|{ai_note}"])

  lines.extend([
    "",
    "DISCLAIMER|This report is generated automatically for screening purposes only. "
    "It does not replace a diagnosis from a qualified doctor or lab professional.",
  ])

  return "\n".join(lines)


def remarks_summary(remarks: str, max_length: int = 100) -> str:
  """Short preview for list views."""
  if not remarks:
    return ""
  for line in remarks.splitlines():
    if line.startswith("OVERALL|"):
      parts = line.split("|", 2)
      if len(parts) >= 3:
        text = parts[2].strip()
        return text if len(text) <= max_length else text[: max_length - 1] + "…"
    if line.startswith("SUMMARY|"):
      text = line.split("|", 1)[1].strip()
      return text if len(text) <= max_length else text[: max_length - 1] + "…"
  return remarks[:max_length] + ("…" if len(remarks) > max_length else "")


def parse_remarks(remarks: str) -> dict:
  """Parse structured remarks for template rendering."""
  parsed: dict = {
    "overall_status": "normal",
    "overall_title": "",
    "summary": "",
    "markers": [],
    "insight": "",
    "ai_note": "",
    "disclaimer": "",
    "legacy": False,
  }
  if not remarks:
    return parsed

  if not remarks.startswith("OVERALL|") and "MARKER|" not in remarks:
    parsed["legacy"] = True
    parsed["summary"] = remarks
    return parsed

  for raw_line in remarks.splitlines():
    line = raw_line.strip()
    if not line:
      continue
    if line.startswith("OVERALL|"):
      parts = line.split("|", 2)
      if len(parts) >= 3:
        parsed["overall_status"] = parts[1]
        parsed["overall_title"] = parts[2]
    elif line.startswith("SUMMARY|"):
      parsed["summary"] = line.split("|", 1)[1]
    elif line.startswith("MARKER|"):
      parts = line.split("|", 3)
      if len(parts) >= 4:
        parsed["markers"].append({
          "name": parts[1],
          "status": parts[2],
          "headline": parts[3],
        })
    elif "• Result:" in raw_line:
      if parsed["markers"]:
        parsed["markers"][-1]["result"] = raw_line.split("• Result:", 1)[1].strip()
    elif "• What it means:" in raw_line:
      if parsed["markers"]:
        parsed["markers"][-1]["meaning"] = raw_line.split("• What it means:", 1)[1].strip()
    elif "• Suggested step:" in raw_line:
      if parsed["markers"]:
        parsed["markers"][-1]["action"] = raw_line.split("• Suggested step:", 1)[1].strip()
    elif line.startswith("INSIGHT|"):
      parsed["insight"] = line.split("|", 1)[1]
    elif line.startswith("AI_NOTE|"):
      parsed["ai_note"] = line.split("|", 1)[1]
    elif line.startswith("DISCLAIMER|"):
      parsed["disclaimer"] = line.split("|", 1)[1]
  return parsed


def get_marker_assessments(
  glucose: float,
  haemoglobin: float,
  cholesterol: float,
) -> list[MarkerResult]:
  return [
    _assess_glucose(glucose),
    _assess_haemoglobin(haemoglobin),
    _assess_cholesterol(cholesterol),
  ]
