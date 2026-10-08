# FitBuddy – AI Fitness Plan Generator

FitBuddy is a web-based AI fitness application.

It generates:

- Personalized 7-day workout plans
- Nutrition/recovery tips
- Updated workout plans based on feedback
- Admin dashboard
- SQLite database storage

---

# TECHNOLOGY

Frontend:
HTML
CSS
Jinja2

Backend:
FastAPI
Python

Database:
SQLite
SQLAlchemy

AI:
Google Gemini

Server:
Uvicorn

---

# PROJECT STRUCTURE

FitBuddy/

app/
    __init__.py
    main.py
    config.py
    database.py
    schemas.py
    routes.py
    gemini_generator.py
    gemini_flash_generator.py
    updated_plan.py

templates/
    base.html
    index.html
    result.html
    admin_login.html
    all_users.html

static/
    css/
        style.css

tests/
    test_app.py

requirements.txt
.env.example
.gitignore
README.md

---

# WINDOWS INSTALLATION

Open the FitBuddy folder in Visual Studio Code.

Open:

Terminal → New Terminal

Create virtual environment:

python -m venv venv

Activate:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

---

# ENVIRONMENT FILE

Copy:

.env.example

to:

.env

Example:

GEMINI_API_KEY=your_api_key_here

GEMINI_WORKOUT_MODEL=gemini-2.5-flash

GEMINI_TIP_MODEL=gemini-2.5-flash

DEMO_MODE=true

ADMIN_KEY=fitbuddy-admin

---

# RUN APPLICATION

Run:

uvicorn app.main:app --reload

Open:

http://127.0.0.1:8000

---

# API DOCUMENTATION

Open:

http://127.0.0.1:8000/docs

---

# HEALTH CHECK

Open:

http://127.0.0.1:8000/health

Expected:

{
    "status": "ok",
    "service": "FitBuddy"
}

---

# ADMIN DASHBOARD

Open:

http://127.0.0.1:8000/view-all-users

Enter:

fitbuddy-admin

Or use whatever ADMIN_KEY is configured in .env.

---

# DEMO MODE

The application supports demo mode.

If:

DEMO_MODE=true

the application can generate sample workout plans without a Gemini API key.

This is useful for testing:

Frontend
Backend
Database
Forms
Feedback
Admin dashboard

---

# REAL GEMINI MODE

For actual AI generation:

DEMO_MODE=false

and configure:

GEMINI_API_KEY=your_real_api_key

---

# TESTING

Run:

pytest

The tests check:

Home page
Health endpoint
Workout generation

---

# DATABASE

The application automatically creates:

fitbuddy.db

when it starts.

Two tables are used:

users

plans

The original workout plan and updated workout plan are stored separately.

---

# MAIN WORKFLOW

1. User opens homepage.

2. User enters:
   - Name
   - User ID
   - Age
   - Weight
   - Goal
   - Workout intensity

3. FastAPI validates the input.

4. Gemini generates a 7-day plan.

5. Gemini generates a nutrition/recovery tip.

6. User and plan are stored in SQLite.

7. Result page displays the plan.

8. User can submit feedback.

9. Gemini updates the plan.

10. Updated plan is saved.

11. Admin can view registered users and plans.

---

# SAFETY

FitBuddy provides general fitness and wellness guidance.

It is not a medical diagnosis or treatment application.

Users should stop exercising if they experience pain,
dizziness, or unusual symptoms and seek appropriate
professional guidance when needed.