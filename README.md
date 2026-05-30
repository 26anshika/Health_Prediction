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

Here are some snapshots of the Health prediction AI Application:
Dashboard - 
<img width="1723" height="915" alt="image" src="https://github.com/user-attachments/assets/d3a1a9eb-e4b0-4e92-930f-df2a45faa729" />
Adding a new Patient-
<img width="1718" height="918" alt="image" src="https://github.com/user-attachments/assets/5f3902f0-a066-470a-817d-44e8d59384fe" />
View Ptient's healt -
<img width="1626" height="903" alt="image" src="https://github.com/user-attachments/assets/781408cc-afe8-4e1a-99e2-b02fcf60b1ed" />

