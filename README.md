# Health Prediction Application

A web application for managing patient contacts and generating AI-assisted health risk remarks from blood test results (glucose, haemoglobin, cholesterol).

Built with **Python (Flask)**, **SQLite**, **Bootstrap 5**, and integration with **WHO GHO** and optional **Hugging Face** ML APIs.

## Features

- Full **CRUD** for patient records
- **Input validation** (email, date of birth, numeric lab values)
- **Persistent storage** via SQLite
- **AI/ML remarks** generated from external health APIs on create/update

## Quick Start

See **[LOCAL_SETUP.md](LOCAL_SETUP.md)** for detailed local installation instructions.

```powershell
cd Health_Prediction
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Visit http://127.0.0.1:5000

## License

Educational / assessment project.
