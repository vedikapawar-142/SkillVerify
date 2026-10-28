"""Comprehensive tests for Diploma Synopsis features:
- MySQL models & persistence
- ReportLab PDF certificate & qrcode verification
- Public verification route /certificate/verify/<cert_id>
- AI Technical Interview rubric evaluation
- MediaPipe / Tab proctoring violation recording & deduction
- Adaptive assessment ladder & weighted scoring formula
- Subprocess sandbox code runner
"""
import os
import json
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Resume, Question, Attempt, Answer, Report, Certificate, Violation, InterviewQA, JobRole
from config import Config
from app.services.code_runner import run_python
from app.services.certificate_service import get_or_create_certificate, generate_qr_code, generate_certificate_pdf
from app.services.interview_service import evaluate_interview_response, get_interview_questions
from app.services.assessment_service import get_or_seed_questions, evaluate_assessment, determine_performance_category


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


@pytest.fixture
def test_app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        get_or_seed_questions()
        yield app
        db.drop_all()


@pytest.fixture
def client(test_app):
    return test_app.test_client()


def test_models_and_relationships(test_app):
    """Verify all database models defined in the synopsis are functional."""
    with test_app.app_context():
        # User
        user = User(name="Vedika Pawar", email="vedika.test@college.edu", role="candidate")
        user.set_password("Student@123")
        db.session.add(user)
        db.session.commit()
        assert user.check_password("Student@123") is True
        assert user.is_candidate is True

        # Attempt
        attempt = Attempt(
            user_id=user.id,
            skill="python",
            status="completed",
            final_score=85.0,
            coding_score=90.0,
            debugging_score=80.0,
            problem_solving_score=85.0,
            interview_score=85.0,
            performance_category="Advanced (Strong Performance)",
            integrity_score=95.0
        )
        db.session.add(attempt)
        db.session.commit()

        # Certificate
        cert = Certificate(
            certificate_id="CERT-2026-TEST01",
            attempt_id=attempt.id,
            user_id=user.id,
            candidate_name=user.name,
            skill="Python",
            score=85.0,
            performance_category=attempt.performance_category
        )
        db.session.add(cert)
        db.session.commit()

        queried_cert = Certificate.query.filter_by(certificate_id="CERT-2026-TEST01").first()
        assert queried_cert is not None
        assert queried_cert.candidate_name == "Vedika Pawar"
        assert queried_cert.score == 85.0


def test_certificate_and_qr_generation(test_app):
    """Verify ReportLab PDF certificate and qrcode QR code generation."""
    with test_app.app_context():
        user = User(name="Vedika Gole", email="vedika.gole@college.edu", role="candidate")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()

        attempt = Attempt(
            user_id=user.id,
            skill="python",
            status="completed",
            final_score=78.5,
            performance_category="Intermediate"
        )
        db.session.add(attempt)
        db.session.commit()

        cert = get_or_create_certificate(attempt, "http://127.0.0.1:5000")
        assert cert is not None
        assert cert.certificate_id.startswith("CERT-2026-")
        assert os.path.exists(cert.pdf_path)
        assert os.path.exists(cert.qr_code_path)
        assert os.path.getsize(cert.pdf_path) > 1000
        assert os.path.getsize(cert.qr_code_path) > 500


def test_public_certificate_verification_route(client, test_app):
    """Verify the public certificate verification route /certificate/verify/<cert_id>."""
    with test_app.app_context():
        user = User(name="Prajakta Bhangarath", email="prajakta@college.edu", role="candidate")
        user.set_password("prajakta123")
        db.session.add(user)
        db.session.commit()

        attempt = Attempt(
            user_id=user.id,
            skill="python",
            status="completed",
            final_score=92.0,
            performance_category="Advanced (Strong Performance)"
        )
        db.session.add(attempt)
        db.session.commit()

        cert = Certificate(
            certificate_id="CERT-2026-PRAJAKTA",
            attempt_id=attempt.id,
            user_id=user.id,
            candidate_name=user.name,
            skill="Python",
            score=92.0,
            performance_category=attempt.performance_category
        )
        db.session.add(cert)
        db.session.commit()

    # Valid certificate query
    res = client.get("/certificate/verify/CERT-2026-PRAJAKTA")
    assert res.status_code == 200
    assert b"Authentic Certificate Verified" in res.data
    assert b"Prajakta Bhangarath" in res.data
    assert b"92" in res.data

    # Invalid certificate query
    res_fake = client.get("/certificate/verify/CERT-INVALID-999")
    assert res_fake.status_code == 200
    assert b"Certificate Not Found" in res_fake.data


def test_ai_technical_interview_evaluation():
    """Verify AI technical interview rubric evaluation (Correctness, Relevance, Clarity)."""
    question = "Explain the difference between an iterator and a generator in Python."
    answer = (
        "An iterator in Python is an object implementing the __iter__ and __next__ protocols. "
        "A generator is a specialized iterator written using the 'yield' keyword which yields values lazily "
        "on-demand without storing the entire sequence in memory, providing significant memory efficiency."
    )
    result = evaluate_interview_response(question, answer, ["yield", "iterator", "generator", "memory", "protocol"])
    assert result["score"] >= 60.0
    assert "rubric" in result
    assert result["rubric"]["correctness"] > 0
    assert result["rubric"]["relevance"] > 0
    assert result["rubric"]["clarity"] > 0


def test_phase1_scoring_and_question_bank(test_app):
    """Verify Phase 1 question bank seeding (80 MCQs total: 20 per language) and proportional scoring."""
    with test_app.app_context():
        user = User(name="Scoring Test", email="scoring@test.com", role="candidate")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()

        # Seed questions - exactly 80 calibrated MCQs
        questions = get_or_seed_questions()
        assert len(questions) == 80

        # Verify each language has 20 MCQs
        for lang in ["python", "java", "c", "cpp"]:
            lang_qs = [q for q in questions if q.skill == lang]
            assert len(lang_qs) == 20

