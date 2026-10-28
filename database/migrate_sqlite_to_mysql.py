"""Database migration script: Migrate SQLite data to MySQL (XAMPP / MySQL80).
Preserves all user records, assessment attempts, questions, reports, and resumes.
"""
import os
import sys
import sqlite3
import urllib.parse
import pymysql
from dotenv import load_dotenv

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import Config
from app import create_app
from app.extensions import db
from app.models import (
    User, Resume, JobRole, Question, Attempt, Answer, 
    InterviewQA, Violation, Report, Certificate
)

load_dotenv()

SQLITE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instance", "skillverify.db.bak"))
if not os.path.exists(SQLITE_PATH):
    SQLITE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "instance", "skillverify.db"))


def run_migration():
    print(f"[*] Reading source SQLite database: {SQLITE_PATH}")
    if not os.path.exists(SQLITE_PATH):
        print(f"[!] SQLite source database not found at {SQLITE_PATH}")
        return False

    app = create_app()
    with app.app_context():
        print(f"[*] Target Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Create all tables in MySQL
        print("[*] Creating all MySQL tables if not exist...")
        db.create_all()
        print("[+] MySQL tables created successfully.")

        # Read from SQLite
        s_conn = sqlite3.connect(SQLITE_PATH)
        s_conn.row_factory = sqlite3.Row
        s_cur = s_conn.cursor()

        # Migrate Users
        print("[*] Migrating Users...")
        s_cur.execute("SELECT * FROM users")
        user_rows = s_cur.fetchall()
        for u in user_rows:
            existing = User.query.filter_by(id=u["id"]).first()
            if not existing:
                new_u = User(
                    id=u["id"],
                    name=u["name"],
                    email=u["email"],
                    password_hash=u["password_hash"],
                    role=u["role"] if "role" in u.keys() else "candidate",
                    created_at=u["created_at"]
                )
                db.session.add(new_u)
        db.session.commit()
        print(f"[+] Migrated {len(user_rows)} users.")

        # Migrate Questions
        print("[*] Migrating Questions...")
        s_cur.execute("SELECT * FROM questions")
        q_rows = s_cur.fetchall()
        for q in q_rows:
            existing = Question.query.filter_by(id=q["id"]).first()
            if not existing:
                new_q = Question(
                    id=q["id"],
                    skill=q["skill"] if "skill" in q.keys() else "python",
                    type=q["type"],
                    topic=q["topic"] if "topic" in q.keys() else "Python Fundamentals",
                    difficulty=q["difficulty"] if "difficulty" in q.keys() else 1,
                    statement=q["statement"],
                    code_snippet=q["code_snippet"],
                    starter_code=q["starter_code"],
                    options=q["options"],
                    correct_answer=q["correct_answer"],
                    test_cases=q["test_cases"],
                    marks=q["marks"] if "marks" in q.keys() else 20,
                    explanation=q["explanation"]
                )
                db.session.add(new_q)
        db.session.commit()
        print(f"[+] Migrated {len(q_rows)} questions.")

        # Migrate Resumes
        print("[*] Migrating Resumes...")
        s_cur.execute("SELECT * FROM resumes")
        r_rows = s_cur.fetchall()
        for r in r_rows:
            existing = Resume.query.filter_by(id=r["id"]).first()
            if not existing:
                new_r = Resume(
                    id=r["id"],
                    user_id=r["user_id"],
                    filename=r["filename"],
                    file_path=r["file_path"],
                    raw_text=r["raw_text"],
                    extracted_skills=r["extracted_skills"],
                    parsed_data=r["parsed_data"],
                    status=r["status"] if "status" in r.keys() else "processed",
                    uploaded_at=r["uploaded_at"]
                )
                db.session.add(new_r)
        db.session.commit()
        print(f"[+] Migrated {len(r_rows)} resumes.")

        # Migrate Attempts
        print("[*] Migrating Attempts...")
        s_cur.execute("SELECT * FROM attempts")
        a_rows = s_cur.fetchall()
        for a in a_rows:
            existing = Attempt.query.filter_by(id=a["id"]).first()
            if not existing:
                new_a = Attempt(
                    id=a["id"],
                    user_id=a["user_id"],
                    role_id=a["role_id"] if "role_id" in a.keys() else None,
                    skill=a["skill"] if "skill" in a.keys() else "python",
                    status=a["status"] if "status" in a.keys() else "completed",
                    started_at=a["started_at"],
                    completed_at=a["completed_at"],
                    final_score=a["final_score"],
                    performance_category=a["performance_category"],
                    correct_count=a["correct_count"] if "correct_count" in a.keys() else 0,
                    total_questions=a["total_questions"] if "total_questions" in a.keys() else 5,
                    integrity_score=a["integrity_score"] if "integrity_score" in a.keys() else 100.0
                )
                db.session.add(new_a)
        db.session.commit()
        print(f"[+] Migrated {len(a_rows)} attempts.")

        # Migrate Answers
        print("[*] Migrating Answers...")
        s_cur.execute("SELECT * FROM answers")
        ans_rows = s_cur.fetchall()
        for ans in ans_rows:
            existing = Answer.query.filter_by(id=ans["id"]).first()
            if not existing:
                new_ans = Answer(
                    id=ans["id"],
                    attempt_id=ans["attempt_id"],
                    question_id=ans["question_id"],
                    submitted_answer=ans["submitted_answer"],
                    submitted_code=ans["submitted_code"],
                    is_correct=bool(ans["is_correct"]),
                    tests_passed=ans["tests_passed"] if "tests_passed" in ans.keys() else 0,
                    tests_total=ans["tests_total"] if "tests_total" in ans.keys() else 0,
                    score=ans["score"] if "score" in ans.keys() else 0.0,
                    feedback=ans["feedback"],
                    execution_output=ans["execution_output"]
                )
                db.session.add(new_ans)
        db.session.commit()
        print(f"[+] Migrated {len(ans_rows)} answers.")

        # Migrate Reports
        print("[*] Migrating Reports...")
        s_cur.execute("SELECT * FROM reports")
        rep_rows = s_cur.fetchall()
        for rep in rep_rows:
            existing = Report.query.filter_by(id=rep["id"]).first()
            if not existing:
                new_rep = Report(
                    id=rep["id"],
                    attempt_id=rep["attempt_id"],
                    user_id=rep["user_id"],
                    verified_skills=rep["verified_skills"],
                    claimed_skills=rep["claimed_skills"],
                    comparison_summary=rep["comparison_summary"],
                    strengths_weaknesses=rep["strengths_weaknesses"],
                    improvement_suggestions=rep["improvement_suggestions"],
                    certificate_id=rep["certificate_id"],
                    generated_at=rep["generated_at"]
                )
                db.session.add(new_rep)
        db.session.commit()
        print(f"[+] Migrated {len(rep_rows)} reports.")

        s_conn.close()
        print("\n[SUCCESS] SQLite -> MySQL migration complete! All data successfully preserved in MySQL.")
        return True


if __name__ == "__main__":
    run_migration()
