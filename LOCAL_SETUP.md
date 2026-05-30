# Local Setup Guide — Health Prediction Application

This guide explains how to run the Health Prediction web application on your Windows, macOS, or Linux machine.

## What You Need

| Requirement | Details |
|-------------|---------|
| **Python** | Version 3.10 or newer ([python.org](https://www.python.org/downloads/)) |
| **Internet** | Required for AI/ML API calls (WHO GHO API; optional Hugging Face API) |
| **Web browser** | Chrome, Firefox, Edge, or similar |
| **Git** (optional) | Only if cloning from GitHub |

No Node.js is required — the frontend uses Bootstrap from a CDN.

## Project Structure

```
Health_Prediction/
  app.py              # Flask application entry point
  config.py           # Configuration (database, API settings)
  models.py           # Database models
  validators.py       # Input validation
  health_service.py   # External API + health prediction logic
  templates/          # HTML pages
  static/css/         # Custom styles
  instance/           # SQLite database (created on first run)
  requirements.txt    # Python dependencies
  .env.example        # Environment variable template (no secrets)
```

## Step-by-Step Setup

### 1. Open a terminal in the project folder

```powershell
cd "c:\Health Prediction\Health_Prediction"
```

### 2. Create a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables (optional)

```powershell
copy .env.example .env
```

Edit `.env` if you want:

- **`HF_API_TOKEN`** — Hugging Face API token for stronger ML-based remarks ([get a free token](https://huggingface.co/settings/tokens)). The app works without it using WHO API + clinical ranges.
- **`SECRET_KEY`** — Change for production-like deployments.

**Important:** Do not commit `.env` to GitHub. It is listed in `.gitignore`.

### 5. Run the application

```powershell
python app.py
```

You should see output similar to:

```
 * Running on http://0.0.0.0:5000
```

Open in your browser: **http://127.0.0.1:5000**

### 6. Use the application

1. Click **Add Patient** or **New Patient**.
2. Enter contact details and blood test values (numeric).
3. Submit — the app validates input, calls health/AI APIs, and saves the record with **Remarks**.
4. Use **View**, **Edit**, or **Delete** on the patient list for full CRUD.

## Sample Test Data

| Field | Example |
|-------|---------|
| Full Name | Jane Doe |
| Date of Birth | 1990-05-15 |
| Email | jane.doe@example.com |
| Glucose | 110 |
| Haemoglobin | 13.2 |
| Cholesterol | 220 |

## Validation Rules

- Email must be a valid format.
- Date of birth cannot be in the future.
- Glucose, haemoglobin, and cholesterol must be non-negative numbers.

## API Integration

On create/update, the app:

1. Calls the **WHO Global Health Observatory API** for health indicator context.
2. Optionally calls the **Hugging Face Inference API** (zero-shot classification) when `HF_API_TOKEN` is set.
3. Writes the combined prediction into the **Remarks** field.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `python` not found | Install Python and ensure “Add to PATH” was checked, or use `py -3` on Windows |
| Port 5000 in use | Set `PORT=5001` then run: `$env:PORT=5001; python app.py` (PowerShell) |
| Module not found | Activate the virtual environment and run `pip install -r requirements.txt` again |
| Slow first AI call | Hugging Face models may “warm up”; retry after a few seconds |
| Database locked | Close other processes using the app; delete `instance/health_prediction.db` only if you accept losing data |

## Before Uploading to GitHub

- Remove or never add `.env` files with real tokens.
- Use `.env.example` for documentation only.
- Confirm `.gitignore` excludes `venv/`, `__pycache__/`, and `.env`.

## Stopping the Server

Press `Ctrl+C` in the terminal where the app is running.
