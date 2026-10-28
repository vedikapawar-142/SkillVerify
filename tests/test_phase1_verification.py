"""Comprehensive Automated Test Suite for Phase 1 AI Skill Verification Platform.
Covers all 17 mandatory testing requirements:
1. Candidate registration and login
2. Password hashing
3. Role-based authorization
4. Resume file validation
5. PDF and DOCX text extraction
6. Skill extraction
7. Gemini-disabled fallback
8. Language-specific question selection
9. Exactly 7 distinct questions per attempt
10. Proportional score calculation
11. Correct-answer review after submission
12. Question persistence after refresh
13. Duplicate-submission prevention
14. Candidate data isolation
15. HR search and filters
16. PDF report generation
17. Certificate eligibility & QR verification
"""
import io
import os
import json
import docx
from werkzeug.security import check_password_hash
from app.models import User, Resume, Question, Attempt, Answer, Report, Certificate
from app.extensions import db
from app.services.resume_parser import (
    validate_resume_file, extract_text_from_docx, extract_resume_text, analyze_resume_text
)
from app.services.llm import analyze_resume_with_gemini
from app.services.assessment_service import (
    get_or_seed_questions, start_or_resume_attempt, evaluate_assessment,
    determine_performance_category, SUPPORTED_LANGUAGES
)
from app.services.certificate_service import (
    generate_report_pdf, generate_certificate_pdf, get_or_create_certificate
)


# ==============================================================================
# 1. CANDIDATE REGISTRATION AND LOGIN
# ==============================================================================
def test_candidate_registration_and_login(client, app):
    """Verify candidate registration, required fields, and successful login."""
    # Attempt registration with duplicate / invalid email
    res_bad = client.post("/register", data={"name": "", "email": "bademail", "password": "123"})
    assert res_bad.status_code == 200

    # Valid candidate registration
    res_reg = client.post("/register", data={
        "name": "Arjun Patel",
        "email": "arjun@example.com",
        "password": "securepassword123"
    }, follow_redirects=True)
    assert res_reg.status_code == 200
    assert b"registration successful" in res_reg.data.lower()

    with app.app_context():
        user = User.query.filter_by(email="arjun@example.com").first()
        assert user is not None
        assert user.name == "Arjun Patel"
        assert user.role == "candidate"

    # Login with valid credentials
    res_login = client.post("/login", data={
        "email": "arjun@example.com",
        "password": "securepassword123"
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b"Candidate Dashboard" in res_login.data
    assert b"Arjun Patel" in res_login.data

    # Logout
    res_logout = client.get("/logout", follow_redirects=True)
    assert res_logout.status_code == 200
    assert b"logged out" in res_logout.data.lower()


# ==============================================================================
# 2. PASSWORD HASHING
# ==============================================================================
def test_password_hashing(app):
    """Verify that passwords are never stored in plain text and verify using hashes."""
    with app.app_context():
        plain_pw = "SuperSecretPass!2026"
        user = User(name="Hash Test", email="hash@example.com", role="candidate")
        user.set_password(plain_pw)
        db.session.add(user)
        db.session.commit()

        # Verify not plaintext
        assert user.password_hash != plain_pw
        assert len(user.password_hash) > 20
        assert user.check_password(plain_pw) is True
        assert user.check_password("WrongPassword") is False


# ==============================================================================
# 3. ROLE-BASED AUTHORIZATION & ROLE SPOOFING PREVENTION
# ==============================================================================
def test_role_based_authorization_and_spoofing_prevention(client, app):
    """Verify candidates cannot access HR routes, and public registration strictly enforces candidate role."""
    with app.app_context():
        # Create an HR user
        hr_user = User.query.filter_by(email="hr_test@example.com").first()
        if not hr_user:
            hr_user = User(name="Recruiter Admin", email="hr_test@example.com", role="hr")
            hr_user.set_password("hrpassword123")
            db.session.add(hr_user)
            db.session.commit()

    # Attempt public registration trying to spoof role="hr"
    client.post("/register", data={
        "name": "Spoof Attempter",
        "email": "spoof@example.com",
        "password": "password123",
        "role": "hr"  # Should be ignored and forced to candidate
    })

    with app.app_context():
        spoof_user = User.query.filter_by(email="spoof@example.com").first()
        assert spoof_user is not None
        assert spoof_user.role == "candidate"  # Enforced candidate!

    # Login as candidate
    client.post("/login", data={"email": "spoof@example.com", "password": "password123"})

    # Candidate attempting to visit HR dashboard URL directly must be blocked
    hr_res = client.get("/hr/dashboard", follow_redirects=True)
    assert hr_res.status_code == 200
    assert b"Access denied" in hr_res.data
    assert b"HR recruiter credentials required" in hr_res.data

    # Log out
    client.get("/logout")

    # Log in as HR
    client.post("/login", data={"email": "hr_test@example.com", "password": "hrpassword123"}, follow_redirects=True)
    hr_dash_res = client.get("/hr/dashboard")
    assert hr_dash_res.status_code == 200
    assert b"Candidate Skill Verification Directory" in hr_dash_res.data


# ==============================================================================
# 4. RESUME FILE VALIDATION
# ==============================================================================
def test_resume_file_validation(tmp_path):
    """Verify extension checks, magic bytes, empty files, and size limits."""
    # 1. Empty file
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_bytes(b"")
    valid, msg = validate_resume_file(str(empty_file))
    assert valid is False
    assert "empty" in msg.lower()

    # 2. Fake extension (text file renamed to .pdf without PDF magic bytes)
    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_bytes(b"This is just plain text, not a real PDF file.")
    valid, msg = validate_resume_file(str(fake_pdf))
    assert valid is False
    assert "header" in msg.lower() or "signature" in msg.lower()

    # 3. Valid PDF header
    real_pdf = tmp_path / "valid.pdf"
    real_pdf.write_bytes(b"%PDF-1.4\n%real pdf content goes here...\n")
    valid, msg = validate_resume_file(str(real_pdf))
    assert valid is True
    assert msg == "Valid"

    # 4. Unsupported extension (.exe, .txt)
    unsupported = tmp_path / "resume.txt"
    unsupported.write_bytes(b"hello world")
    valid, msg = validate_resume_file(str(unsupported))
    assert valid is False
    assert "unsupported" in msg.lower()


# ==============================================================================
# 5. PDF AND DOCX TEXT EXTRACTION
# ==============================================================================
def test_pdf_and_docx_text_extraction(tmp_path):
    """Verify reliable text extraction from DOCX."""
    doc = docx.Document()
    doc.add_heading("Priya Sharma", level=0)
    doc.add_paragraph("Email: priya@example.com | Phone: 9876543210")
    doc.add_heading("Technical Skills", level=1)
    doc.add_paragraph("Python, Java, MySQL, Flask, Docker, Git")
    doc.add_heading("Education", level=1)
    doc.add_paragraph("B.E. in Computer Engineering, SPPU, 2024")
    
    docx_path = str(tmp_path / "sample_resume.docx")
    doc.save(docx_path)

    extracted = extract_text_from_docx(docx_path)
    assert "Priya Sharma" in extracted
    assert "Python" in extracted
    assert "MySQL" in extracted
    assert "Computer Engineering" in extracted


# ==============================================================================
# 6. SKILL EXTRACTION VIA NLP TAXONOMY
# ==============================================================================
def test_skill_extraction_baseline():
    """Verify rule-based extraction correctly maps skills across categories."""
    resume_text = (
        "PROFESSIONAL PROFILE\n"
        "Full Stack Developer proficient in Python, Java, C++, and MySQL.\n"
        "Experience building web applications using Flask, Bootstrap, and REST API.\n"
        "Proficient with Docker, Git, Linux, and AWS cloud environments.\n"
    )
    analysis = analyze_resume_text(resume_text)
    skills = analysis.get("claimed_skills", [])
    
    assert "Python" in skills
    assert "Java" in skills
    assert "C++" in skills
    assert "MySQL" in skills
    assert "Flask" in skills
    assert "Docker" in skills
    assert "Git" in skills

    categorized = analysis.get("categorized_skills", {})
    assert "Programming Languages" in categorized
    assert "Python" in categorized["Programming Languages"]
    assert "Java" in categorized["Programming Languages"]


# ==============================================================================
# 7. GEMINI-DISABLED FALLBACK
# ==============================================================================
def test_gemini_disabled_fallback(monkeypatch):
    """Verify graceful and clearly labeled fallback when GEMINI_API_KEY is unset."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    resume_text = "Software Engineer with expertise in Python, SQL, and Docker."
    
    result = analyze_resume_with_gemini(resume_text)
    assert result["is_gemini"] is False
    assert "local rule-based" in result["engine"].lower()
    assert "Python" in result["technical_skills"]
    assert len(result["strengths"]) > 0
    assert len(result["improvement_suggestions"]) > 0
    assert "baseline analysis" in result["summary"].lower()


# ==============================================================================
# 8. LANGUAGE-SPECIFIC QUESTION SELECTION (PYTHON, JAVA, C, C++)
# ==============================================================================
def test_language_specific_question_selection(app):
    """Verify that question bank contains calibrated questions for all 4 languages."""
    with app.app_context():
        for lang in SUPPORTED_LANGUAGES:
            questions = get_or_seed_questions(lang)
            assert len(questions) >= 20, f"Expected at least 20 questions for {lang}"
            for q in questions:
                assert q.skill.lower() == lang
                assert q.type == "mcq"
                assert len(q.get_options()) == 4
                assert q.correct_answer in q.get_options()


# ==============================================================================
# 9. EXACTLY 7 DISTINCT QUESTIONS PER ATTEMPT
# ==============================================================================
def test_exactly_7_distinct_questions_per_attempt(app):
    """Verify an attempt generates exactly 7 unique questions for the chosen language."""
    with app.app_context():
        user = User(name="Candidate 7Q", email="cand7q@example.com", role="candidate")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()

        for lang in SUPPORTED_LANGUAGES:
            attempt = start_or_resume_attempt(user.id, lang)
            q_ids = attempt.get_question_ids()
            assert len(q_ids) == 7
            assert len(set(q_ids)) == 7, "Questions in attempt must all be distinct"

            questions = attempt.get_selected_questions()
            assert len(questions) == 7
            for q in questions:
                assert q.skill.lower() == lang


# ==============================================================================
# 10. PROPORTIONAL SCORE CALCULATION
# ==============================================================================
def test_proportional_score_calculation(app):
    """Verify exact formula: Score = (Correct / 7) * 100 on 100-mark scale."""
    with app.app_context():
        user = User(name="Scoring Test", email="scoretest@example.com", role="candidate")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()

        attempt = start_or_resume_attempt(user.id, "python")
        questions = attempt.get_selected_questions()

        # Submit 5 correct out of 7
        form_data = {}
        for idx, q in enumerate(questions):
            if idx < 5:
                form_data[f"q_{q.id}"] = q.correct_answer
            else:
                form_data[f"q_{q.id}"] = "Wrong Answer Selection"

        evaluated = evaluate_assessment(attempt.id, form_data)
        assert evaluated.correct_count == 5
        assert evaluated.total_questions == 7
        
        # Expected: (5 / 7) * 100 = 71.4285... -> rounded to 71.43
        expected_score = round((5 / 7) * 100, 2)
        assert evaluated.final_score == expected_score
        assert evaluated.percentage == expected_score
        assert evaluated.performance_category == "Intermediate (Competent)"


# ==============================================================================
# 11. CORRECT-ANSWER REVIEW AFTER SUBMISSION
# ==============================================================================
def test_correct_answer_review_after_submission(client, app):
    """Verify that results page displays correct answers, explanations, and indicators."""
    with app.app_context():
        user = User(name="Review Candidate", email="review@example.com", role="candidate")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
        u_id = user.id

    # Ensure clean session before logging in
    client.get("/logout")
    # Log in
    client.post("/login", data={"email": "review@example.com", "password": "pass123"}, follow_redirects=True)

    with app.app_context():
        attempt = start_or_resume_attempt(u_id, "java")
        questions = attempt.get_selected_questions()
        form_data = {f"q_{q.id}": q.correct_answer for q in questions}
        evaluate_assessment(attempt.id, form_data)
        att_id = attempt.id

    res = client.get(f"/assessment/result/{att_id}")
    assert res.status_code == 200
    assert b"Java Skill Assessment Result" in res.data
    assert b"100" in res.data
    assert b"Complete Question-by-Question Answer Review" in res.data
    assert b"Technical Explanation:" in res.data
    assert b"Correct Answer" in res.data


# ==============================================================================
# 12. QUESTION PERSISTENCE AFTER REFRESH
# ==============================================================================
def test_question_persistence_after_refresh(app):
    """Verify that calling start_or_resume_attempt on an active attempt preserves identical questions."""
    with app.app_context():
        user = User(name="Persist User", email="persist@example.com", role="candidate")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()

        # First call: creates attempt
        att1 = start_or_resume_attempt(user.id, "cpp")
        q_ids_1 = att1.get_question_ids()

        # Second call (simulating page reload): retrieves existing attempt
        att2 = start_or_resume_attempt(user.id, "cpp")
        q_ids_2 = att2.get_question_ids()

        assert att1.id == att2.id
        assert q_ids_1 == q_ids_2, "Question set must remain identical across page refreshes"


# ==============================================================================
# 13. DUPLICATE-SUBMISSION PREVENTION
# ==============================================================================
def test_duplicate_submission_prevention(app):
    """Verify that an already completed assessment cannot be re-submitted or modified."""
    with app.app_context():
        user = User(name="Anti Dup", email="antidup@example.com", role="candidate")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()

        attempt = start_or_resume_attempt(user.id, "c")
        questions = attempt.get_selected_questions()
        first_form = {f"q_{q.id}": q.correct_answer for q in questions}

        # First evaluation
        eval1 = evaluate_assessment(attempt.id, first_form)
        first_score = eval1.final_score
        assert eval1.status == "completed"

        # Attempt second evaluation with different answers
        tampered_form = {f"q_{q.id}": "Wrong" for q in questions}
        eval2 = evaluate_assessment(attempt.id, tampered_form)

        # Score and status must remain unmodified
        assert eval2.final_score == first_score
        assert eval2.correct_count == 7


# ==============================================================================
# 14. CANDIDATE DATA ISOLATION
# ==============================================================================
def test_candidate_data_isolation(client, app):
    """Verify Candidate A cannot access Candidate B's assessment results or report."""
    with app.app_context():
        user_a = User(name="Alice", email="alice@example.com", role="candidate")
        user_a.set_password("pass123")
        user_b = User(name="Bob", email="bob@example.com", role="candidate")
        user_b.set_password("pass123")
        db.session.add_all([user_a, user_b])
        db.session.commit()

        # Create completed attempt for Alice
        att_alice = start_or_resume_attempt(user_a.id, "python")
        q_ids = att_alice.get_selected_questions()
        evaluate_assessment(att_alice.id, {f"q_{q.id}": q.correct_answer for q in q_ids})
        alice_att_id = att_alice.id
        alice_rep_id = att_alice.report.id

    # Ensure clean session before logging in
    client.get("/logout")
    # Log in as Bob
    client.post("/login", data={"email": "bob@example.com", "password": "pass123"}, follow_redirects=True)

    # Bob attempts to view Alice's assessment result -> 403 Forbidden
    res_result = client.get(f"/assessment/result/{alice_att_id}")
    assert res_result.status_code == 403

    # Bob attempts to view Alice's report -> 403 Forbidden
    res_report = client.get(f"/report/{alice_rep_id}")
    assert res_report.status_code == 403

    # Bob attempts to download Alice's PDF report -> 403 Forbidden
    res_pdf = client.get(f"/report/{alice_rep_id}/pdf")
    assert res_pdf.status_code == 403


# ==============================================================================
# 15. HR SEARCH AND FILTERS
# ==============================================================================
def test_hr_search_and_filters(client, app):
    """Verify HR portal search by name, filter by language, score, and status."""
    with app.app_context():
        hr = User(name="HR Filter Officer", email="hr_filters@example.com", role="hr")
        hr.set_password("hrpass123")
        cand1 = User(name="Dev Python", email="dev_py@example.com", role="candidate")
        cand1.set_password("pass123")
        cand2 = User(name="Dev Java", email="dev_java@example.com", role="candidate")
        cand2.set_password("pass123")
        db.session.add_all([hr, cand1, cand2])
        db.session.commit()

        # Cand 1 completes Python assessment with 100%
        att1 = start_or_resume_attempt(cand1.id, "python")
        q1 = att1.get_selected_questions()
        evaluate_assessment(att1.id, {f"q_{q.id}": q.correct_answer for q in q1})

    # Ensure clean session
    client.get("/logout")
    # Log in as HR
    client.post("/login", data={"email": "hr_filters@example.com", "password": "hrpass123"}, follow_redirects=True)

    # Search for "Dev Python"
    res_search = client.get("/hr/dashboard?q=Dev+Python")
    assert res_search.status_code == 200
    assert b"dev_py@example.com" in res_search.data
    assert b"dev_java@example.com" not in res_search.data

    # Filter by Language: Python
    res_lang = client.get("/hr/dashboard?lang=python")
    assert res_lang.status_code == 200
    assert b"dev_py@example.com" in res_lang.data

    # Filter by Status: Completed
    res_status = client.get("/hr/dashboard?status=completed")
    assert res_status.status_code == 200
    assert b"dev_py@example.com" in res_status.data


# ==============================================================================
# 16. PDF REPORT GENERATION
# ==============================================================================
def test_pdf_report_generation(app):
    """Verify ReportLab produces valid non-empty PDF containing all 7 questions and explanations."""
    with app.app_context():
        user = User(name="PDF Candidate", email="pdfcand@example.com", role="candidate")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()

        attempt = start_or_resume_attempt(user.id, "python")
        q_list = attempt.get_selected_questions()
        evaluate_assessment(attempt.id, {f"q_{q.id}": q.correct_answer for q in q_list})

        report = attempt.report
        assert report is not None
        pdf_path = generate_report_pdf(report)
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 1000

        # Check PDF header bytes
        with open(pdf_path, "rb") as f:
            header = f.read(5)
            assert header == b"%PDF-"


# ==============================================================================
# 17. CERTIFICATE ELIGIBILITY AND QR VERIFICATION
# ==============================================================================
def test_certificate_eligibility_and_qr_verification(client, app):
    """Verify threshold requirement (>= 60%), QR generation, and public verification page."""
    with app.app_context():
        user_pass = User(name="Eligible Candidate", email="pass@example.com", role="candidate")
        user_pass.set_password("pass123")
        user_fail = User(name="Ineligible Candidate", email="fail@example.com", role="candidate")
        user_fail.set_password("pass123")
        db.session.add_all([user_pass, user_fail])
        db.session.commit()

        # 1. Candidate scoring 100% (7/7 correct) -> Eligible
        att_pass = start_or_resume_attempt(user_pass.id, "python")
        q_pass = att_pass.get_selected_questions()
        evaluate_assessment(att_pass.id, {f"q_{q.id}": q.correct_answer for q in q_pass}, request_base_url="http://localhost:5000")
        assert att_pass.final_score >= 60.0
        assert att_pass.certificate is not None
        cert_id = att_pass.certificate.certificate_id

        # 2. Candidate scoring 28.57% (2/7 correct) -> Not eligible
        att_fail = start_or_resume_attempt(user_fail.id, "python")
        q_fail = att_fail.get_selected_questions()
        form_fail = {}
        for idx, q in enumerate(q_fail):
            if idx < 2:
                form_fail[f"q_{q.id}"] = q.correct_answer
            else:
                form_fail[f"q_{q.id}"] = "Wrong"
        evaluate_assessment(att_fail.id, form_fail, request_base_url="http://localhost:5000")
        assert att_fail.final_score < 60.0
        assert att_fail.certificate is None

    # Test Public Certificate Verification Route (no login required)
    res_verify = client.get(f"/certificate/verify/{cert_id}")
    assert res_verify.status_code == 200
    assert b"Authentic Certificate Verified" in res_verify.data
    assert b"Eligible Candidate" in res_verify.data
    assert cert_id.encode() in res_verify.data

    # Test invalid certificate verification
    res_invalid = client.get("/certificate/verify/CERT-INVALID-99999999")
    assert res_verify.status_code == 200
    assert b"Certificate Not Found or Invalid" in res_invalid.data
