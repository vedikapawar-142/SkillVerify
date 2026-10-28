# AI Skill Verification Platform (Phase 1)

> *"Verifying candidate technical skills by contrasting resume claims against empirical, objective assessment performance."*

A production-grade web application built with **Python 3, Flask, MySQL (via XAMPP), SQLAlchemy, Bootstrap 5, ReportLab, and Google Gemini API**.

---

## 1. System Overview

The **AI Skill Verification Platform** bridges the gap between claimed technical skills on candidate resumes and verified competency. The platform supports two core roles:

- **Candidate Role:**
  1. Register and securely log in.
  2. Upload resume files (`.pdf` and `.docx`) with validation and secure server-side parsing.
  3. Review extracted technical skills, categorized taxonomy, and optional Google Gemini AI insights.
  4. Select preferred programming language from **Python, Java, C, or C++**.
  5. Attempt an interactive **7-question technical MCQ assessment** drawn randomly from a calibrated 20-question bank per language.
  6. Review question results immediately after submission, including selected answer, correct answer, status, and technical explanation.
  7. Access evidence-based skill comparison and targeted improvement suggestions.
  8. Download vector **PDF assessment reports** and earn **verifiable PDF certificates** (at $\ge 60\%$ score) with scannable QR verification.
- **HR Recruiter Role:**
  1. Access protected HR portal via dedicated login (`/hr/login`).
  2. Search candidates by name, email, or resume skills.
  3. Filter directory by programming language, score ranges, and pass/fail status.
  4. Inspect individual candidate profiles, complete assessment histories, claimed vs. assessed skill comparisons, and download candidate resumes.

---

## 2. Key Architecture & Features

### Core Modules
1. **Candidate Authentication & RBAC:**
   - Public registration strictly assigns `role='candidate'`.
   - HR access is strictly protected on the server side (`@hr_required` decorator); candidates cannot access HR routes.
   - Secure password hashing using Werkzeug `scrypt`.
   - Comprehensive session management with flash messaging.
2. **HR Account Administration:**
   - Dedicated CLI tool (`create_hr.py` and `flask create-hr`) to securely provision HR accounts without public registration vulnerabilities.
3. **Resume Processing & Skill Extraction:**
   - Validates file extensions (`.pdf`, `.docx`) and file magic bytes (`%PDF-`, `PK\x03\x04`).
   - Text extraction via `PyPDF2` (PDF) and `python-docx` (DOCX).
   - Local explainable rule-based NLP parser using an extensive programming taxonomy.
   - Graceful fallback for unreadable, scanned, or empty documents without fabricated results.
4. **Google Gemini AI Integration:**
   - Reads `GEMINI_API_KEY` from environment variables.
   - Returns structured JSON: technical skills, strengths, missing evidence, improvement suggestions, and executive summary.
   - Automatic, transparent fallback labeled `Local Rule-Based Parser (Gemini API key not configured)` when the API key is not set or network is unreachable.
5. **Technical MCQ Assessment Engine (4 Languages, 80 Questions Total):**
   - **4 Supported Languages:** Python, Java, C, C++.
   - **Calibrated Question Bank:** Exactly 20 distinct MCQs per language (80 MCQs total) covering data types, operators, loops, functions, OOP, memory, pointers, and debugging.
   - **7-Question MCQ Workflow:** Every new attempt randomly selects 7 distinct questions from the candidate's chosen language.
   - **Attempt Persistence:** Selected question IDs are saved in MySQL; refreshing or reopening never changes the question set.
   - **Candidate Navigation:** 1-to-7 palette showing answered/unanswered status, allows modifying answers before final submission, and presents a confirmation modal.
   - **Anti-Duplicate Submission:** Prevents repeated scoring or score inflation.
   - **Proportional Scoring:** $\text{Score} = \left(\frac{\text{Correct Answers}}{7}\right) \times 100$, stored accurately and rounded to 2 decimal places for display.
6. **Post-Submission Answer Review:**
   - Shows all 7 questions, candidate's chosen answer, the correct answer, correct/incorrect status badges, and technical explanations.
   - Candidate can revisit completed assessment results at any time.
7. **Skill Comparison & Improvement Suggestions:**
   - Cautious, evidence-based contrast between claimed resume skills and assessment score.
   - Topic-specific improvement recommendations based on candidate's actual errors.
8. **ReportLab PDF Assessment Report & QR Verification:**
   - Downloadable vector PDF report containing assessment breakdown, comparison, and recommendations.
   - Landscape vector PDF certificate issued when score $\ge 60\%$.
   - Embedded QR code linking to public verification endpoint: `/certificate/verify/<cert_id>`.

---

## 3. Technology Stack

- **Operating System:** Windows 10 / 11
- **Backend Framework:** Python 3.11+, Flask 3.1+
- **Database:** MySQL 8.0 through XAMPP
- **Database Driver & ORM:** PyMySQL, Flask-SQLAlchemy / SQLAlchemy 2.0+
- **Authentication:** Flask Sessions, Flask-Login, Werkzeug Security
- **Frontend:** Jinja2, HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons
- **Document Extraction:** PyPDF2 (PDF), python-docx (DOCX)
- **AI Integration:** Google Gemini API (`gemini-1.5-flash`)
- **PDF Generation:** ReportLab
- **QR Code Generation:** Python `qrcode`, Pillow
- **Testing:** pytest

---

## 4. Installation & Setup Guide (Windows PowerShell)

Follow these exact steps in Windows PowerShell to set up and run the platform.

### Step 1: Open Windows PowerShell & Navigate to Project

```powershell
cd "C:\Users\HP\Downloads\ai-skill-verification-phase11 final"
```

### Step 2: Create and Activate Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*(If PowerShell script execution is restricted, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first).*

### Step 3: Install Required Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Configure MySQL in XAMPP

1. Open the **XAMPP Control Panel**.
2. Click **Start** next to **MySQL** (and Apache if desired).
3. Confirm MySQL is running on port **3306**.
4. Open PowerShell or phpMyAdmin to create the database:

```powershell
# Using MySQL command line in XAMPP:
C:\xampp\mysql\bin\mysql.exe -u root -e "CREATE DATABASE IF NOT EXISTS skillverify CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Step 5: Configure Environment Variables (`.env`)

Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` in VS Code or Notepad and verify your credentials:

```ini
SECRET_KEY=dev-secret-key-phase1-verification-2026
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@127.0.0.1:3306/skillverify?charset=utf8mb4
# If root has NO password in XAMPP, use:
# DATABASE_URL=mysql+pymysql://root:@127.0.0.1:3306/skillverify?charset=utf8mb4

GEMINI_API_KEY=
CERTIFICATE_THRESHOLD=60.0
```

### Step 6: Initialize Database & Seed 80-Question Bank

Run the following command to automatically create all MySQL tables and seed the 80 calibrated MCQs (20 Python, 20 Java, 20 C, 20 C++):

```powershell
python -c "from app import create_app; create_app()"
```

### Step 7: Create an HR Recruiter Account

Use the CLI script to create an authorized HR account:

```powershell
python create_hr.py --name "HR Recruiter" --email "hr@skillverify.com" --password "hr123456"
```

*(Alternatively, use the Flask CLI: `flask create-hr --name "HR Recruiter" --email "hr@skillverify.com" --password "hr123456"`)*

### Step 8: Run the Application

```powershell
python run.py
```

The application will start at:
- **Candidate Portal:** [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **HR Login Portal:** [http://127.0.0.1:5000/hr/login](http://127.0.0.1:5000/hr/login)

---

## 5. Running Automated Tests

Run the full pytest suite (35 automated unit and end-to-end tests covering all 17 specification areas):

```powershell
.\venv\Scripts\python.exe -m pytest -v
```

Expected output:
```
======================== 35 passed in ~9s ========================
```

To run individual test modules:
```powershell
# Phase 1 Verification suite (all 17 functional requirements)
pytest tests/test_phase1_verification.py -v

# Full Workflow integration test
pytest tests/test_full_workflow.py -v

# End-to-end simulation
pytest tests/test_live_simulation.py -v
```

---

## 6. Default Demo Credentials

For quick evaluation and testing:

| Role | Email | Password | Access URL |
|---|---|---|---|
| **HR Recruiter** | `hr@skillverify.com` | `hr123456` | `/hr/login` |
| **Candidate** | Register new account at `/register` or login at `/login` |

---

## 7. Directory Structure

```
ai-skill-verification/
├── app/
│   ├── __init__.py               # Flask app factory, CLI commands, DB initialization
│   ├── models.py                 # SQLAlchemy models (User, Resume, Question, Attempt, etc.)
│   ├── extensions.py             # SQLAlchemy and LoginManager instances
│   ├── routes/
│   │   ├── auth.py               # Candidate register/login, HR login, RBAC decorators
│   │   └── main.py               # Assessment workflow, results review, PDF downloads, HR portal
│   ├── services/
│   │   ├── question_bank_data.py # Master 80 calibrated MCQs (Python, Java, C, C++)
│   │   ├── assessment_service.py # Random 7-question sampling, persistence, scoring
│   │   ├── resume_parser.py      # PDF/DOCX extraction, magic-byte checks, skill taxonomy
│   │   ├── llm.py                # Gemini API integration and local rule-based fallback
│   │   └── certificate_service.py# ReportLab PDF report, vector certificate, QR generator
│   └── templates/                # Bootstrap 5 responsive templates
│       ├── base.html
│       ├── index.html
│       ├── register.html         # Candidate-only public registration
│       ├── login.html            # Candidate login
│       ├── hr_login.html         # Protected HR login
│       ├── dashboard.html        # Candidate dashboard
│       ├── hr_dashboard.html     # HR directory with search and multi-filter
│       ├── hr_candidate_detail.html
│       ├── assessment_instructions.html # Language selector (Python, Java, C, C++)
│       ├── assessment_take.html  # 7-question interactive assessment with 1-7 palette
│       ├── assessment_result.html# Complete 7-question review with answers & explanations
│       ├── certificate_verify.html # Public QR code verification page
│       └── report_detail.html
├── config.py                     # Configuration loader with explicit .env path resolution
├── create_hr.py                  # Standalone CLI script for HR provisioning
├── run.py                        # Application entry point
├── requirements.txt              # Production Python package dependencies
├── .env.example                  # Environment variable configuration template
└── tests/                        # Comprehensive automated test suite
    ├── conftest.py
    ├── test_phase1_verification.py # 17 required specification tests
    ├── test_full_workflow.py       # Integration tests
    ├── test_live_simulation.py     # Live end-to-end simulation
    ├── test_smoke.py
    └── test_synopsis_features.py
```
