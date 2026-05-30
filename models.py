from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Patient(db.Model):
  __tablename__ = "patients"

  id = db.Column(db.Integer, primary_key=True)
  full_name = db.Column(db.String(120), nullable=False)
  date_of_birth = db.Column(db.Date, nullable=False)
  email = db.Column(db.String(120), nullable=False)
  glucose = db.Column(db.Float, nullable=False)
  haemoglobin = db.Column(db.Float, nullable=False)
  cholesterol = db.Column(db.Float, nullable=False)
  remarks = db.Column(db.Text, nullable=True)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(
    db.DateTime,
    default=datetime.utcnow,
    onupdate=datetime.utcnow,
  )

  @property
  def age(self) -> int:
    today = date.today()
    years = today.year - self.date_of_birth.year
    if (today.month, today.day) < (
      self.date_of_birth.month,
      self.date_of_birth.day,
    ):
      years -= 1
    return years

  def to_dict(self) -> dict:
    return {
      "id": self.id,
      "full_name": self.full_name,
      "date_of_birth": self.date_of_birth.isoformat(),
      "email": self.email,
      "glucose": self.glucose,
      "haemoglobin": self.haemoglobin,
      "cholesterol": self.cholesterol,
      "remarks": self.remarks,
      "age": self.age,
      "created_at": self.created_at.isoformat() if self.created_at else None,
      "updated_at": self.updated_at.isoformat() if self.updated_at else None,
    }
