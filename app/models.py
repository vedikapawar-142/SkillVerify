"""Database models for AI Skill Verification Platform.
Aligned with Phase 1 Master Architecture:
- Users (candidate / hr / admin)
- Resumes (raw text, parsed data, extracted claimed skills)
- Question Bank (80 MCQs: 20 Python, 20 Java, 20 C, 20 C++)
- Attempts (Language, 7 randomized questions, score out of 100, persistence across refresh)
- Answers (Selected options, correctness, explanations)
- Reports (Empirical vs claimed skill comparison, improvement suggestions)
- Certificates (Verifiable credentials with QR verification)
"""
from datetime import datetime
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="candidate")  # candidate / hr / admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    resumes = db.relationship("Resume", backref="user", cascade="all, delete-orphan", lazy=True)
    attempts = db.relationship("Attempt", backref="user", cascade="all, delete-orphan", lazy=True)
    reports = db.relationship("Report", backref="user", cascade="all, delete-orphan", lazy=True)
    certificates = db.relationship("Certificate", backref="user", cascade="all, delete-orphan", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_candidate(self):
        return self.role == "candidate"

    @property
    def is_hr(self):
        return self.role == "hr"

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def latest_resume(self):
        return Resume.query.filter_by(user_id=self.id).order_by(Resume.uploaded_at.desc()).first()

    @property
    def latest_attempt(self):
        return Attempt.query.filter_by(user_id=self.id, status="completed").order_by(Attempt.completed_at.desc()).first()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Resume(db.Model):
    __tablename__ = "resumes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    filename = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    raw_text = db.Column(db.Text)
    extracted_skills = db.Column(db.Text)  # JSON string of claimed skill names
    parsed_data = db.Column(db.Text)       # JSON string of complete parsed resume structure
    status = db.Column(db.String(30), default="processed")  # uploaded / processed / reviewed
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_skills_list(self):
        if not self.extracted_skills:
            return []
        try:
            return json.loads(self.extracted_skills)
        except Exception:
            return []

    def get_parsed_data(self):
        if not self.parsed_data:
            return {}
        try:
            return json.loads(self.parsed_data)
        except Exception:
            return {}


class JobRole(db.Model):
    __tablename__ = "job_roles"
    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    required_skills = db.Column(db.Text)  # JSON string list of required skills
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_required_skills(self):
        if not self.required_skills:
            return []
        try:
            return json.loads(self.required_skills)
        except Exception:
            return []


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.String(60), nullable=False, default="python", index=True)  # python / java / c / cpp
    type = db.Column(db.String(30), nullable=False, default="mcq")                  # mcq
    topic = db.Column(db.String(100), default="General")
    difficulty = db.Column(db.Integer, nullable=False, default=1, index=True)       # 1=Easy 2=Medium 3=Hard
    statement = db.Column(db.Text, nullable=False)
    code_snippet = db.Column(db.Text)
    starter_code = db.Column(db.Text)
    options = db.Column(db.Text)                                                    # JSON array of 4 options
    correct_answer = db.Column(db.Text)                                             # Exact matching option text
    test_cases = db.Column(db.Text)
    marks = db.Column(db.Integer, default=100)
    explanation = db.Column(db.Text)

    def get_options(self):
        if not self.options:
            return []
        try:
            return json.loads(self.options)
        except Exception:
            return []

    @property
    def language_display(self):
        mapping = {
            "python": "Python",
            "java": "Java",
            "c": "C",
            "cpp": "C++"
        }
        return mapping.get(self.skill.lower(), self.skill.title())


class Attempt(db.Model):
    __tablename__ = "attempts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("job_roles.id"), nullable=True)
    skill = db.Column(db.String(60), default="python")                              # python / java / c / cpp
    status = db.Column(db.String(20), default="in_progress")                        # in_progress / completed
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Phase 1: 7-Question MCQ Assessment Marks & Scoring
    question_ids = db.Column(db.Text, nullable=True)                               # JSON array of selected 7 question IDs
    correct_count = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=7)
    final_score = db.Column(db.Float, default=0.0)                                 # (correct_count / 7.0) * 100.0
    percentage = db.Column(db.Float, default=0.0)
    max_score = db.Column(db.Float, default=100.0)
    performance_category = db.Column(db.String(50))                                # Advanced / Intermediate / Developing / Needs Improvement

    # Legacy fields retained for backwards compatibility with database
    coding_score = db.Column(db.Float, default=0.0)
    debugging_score = db.Column(db.Float, default=0.0)
    problem_solving_score = db.Column(db.Float, default=0.0)
    interview_score = db.Column(db.Float, default=0.0)
    integrity_score = db.Column(db.Float, default=100.0)
    adaptive_path = db.Column(db.Text)

    # Relationships
    answers = db.relationship("Answer", backref="attempt", cascade="all, delete-orphan", lazy=True)
    report = db.relationship("Report", backref="attempt", uselist=False, cascade="all, delete-orphan", lazy=True)
    violations = db.relationship("Violation", backref="attempt", cascade="all, delete-orphan", lazy=True)
    interview_qas = db.relationship("InterviewQA", backref="attempt", cascade="all, delete-orphan", lazy=True)
    certificate = db.relationship("Certificate", backref="attempt", uselist=False, cascade="all, delete-orphan", lazy=True)

    def get_question_ids(self):
        if not self.question_ids:
            return []
        try:
            return json.loads(self.question_ids)
        except Exception:
            return []

    def get_selected_questions(self):
        """Return the 7 questions in their preserved order for this attempt."""
        q_ids = self.get_question_ids()
        if not q_ids:
            # Fallback: questions referenced in answers
            answers = Answer.query.filter_by(attempt_id=self.id).all()
            return [a.question for a in answers if a.question]
        
        # Preserve exact saved sequence
        questions_dict = {q.id: q for q in Question.query.filter(Question.id.in_(q_ids)).all()}
        return [questions_dict[qid] for qid in q_ids if qid in questions_dict]

    @property
    def language_display(self):
        mapping = {
            "python": "Python",
            "java": "Java",
            "c": "C",
            "cpp": "C++"
        }
        return mapping.get((self.skill or "python").lower(), (self.skill or "Python").title())

    @property
    def incorrect_count(self):
        return max(0, self.total_questions - self.correct_count)


class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("attempts.id"), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    submitted_answer = db.Column(db.Text)                              # Candidate selected option
    submitted_code = db.Column(db.Text)                                # Optional code block
    is_correct = db.Column(db.Boolean, default=False)
    tests_passed = db.Column(db.Integer, default=0)
    tests_total = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text)
    execution_output = db.Column(db.Text)
    execution_engine = db.Column(db.String(50), default="MCQ Evaluator")

    question = db.relationship("Question", lazy=True)


class InterviewQA(db.Model):
    __tablename__ = "interview_qa"
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("attempts.id"), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    answer_text = db.Column(db.Text)
    score = db.Column(db.Float, default=0.0)
    feedback = db.Column(db.Text)
    rubric_evaluation = db.Column(db.Text)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Violation(db.Model):
    __tablename__ = "violations"
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("attempts.id"), nullable=False, index=True)
    type = db.Column(db.String(40), nullable=False)
    details = db.Column(db.String(255))
    deduction = db.Column(db.Float, default=5.0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    snapshot_path = db.Column(db.String(255))


class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("attempts.id"), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    verified_skills = db.Column(db.Text)              # JSON: assessed skills & verification outcome
    claimed_skills = db.Column(db.Text)               # JSON: claimed skills from resume
    comparison_summary = db.Column(db.Text)           # JSON: comparison analysis details
    strengths_weaknesses = db.Column(db.Text)         # JSON: topic breakdowns
    improvement_suggestions = db.Column(db.Text)     # JSON: personalized recommendations
    certificate_id = db.Column(db.String(60), unique=True, index=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_verified_skills(self):
        if not self.verified_skills:
            return {}
        try:
            return json.loads(self.verified_skills)
        except Exception:
            return {}

    def get_claimed_skills(self):
        if not self.claimed_skills:
            return []
        try:
            return json.loads(self.claimed_skills)
        except Exception:
            return []

    def get_comparison(self):
        if not self.comparison_summary:
            return {}
        try:
            return json.loads(self.comparison_summary)
        except Exception:
            return {}

    def get_strengths_weaknesses(self):
        if not self.strengths_weaknesses:
            return {}
        try:
            return json.loads(self.strengths_weaknesses)
        except Exception:
            return {}

    def get_improvement_suggestions(self):
        if not self.improvement_suggestions:
            return []
        try:
            return json.loads(self.improvement_suggestions)
        except Exception:
            return []


class Certificate(db.Model):
    __tablename__ = "certificates"
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(60), unique=True, nullable=False, index=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("attempts.id"), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    candidate_name = db.Column(db.String(120), nullable=False)
    skill = db.Column(db.String(60), nullable=False, default="Python")
    score = db.Column(db.Float, nullable=False)
    performance_category = db.Column(db.String(50), nullable=False)
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    qr_code_path = db.Column(db.String(255))
    pdf_path = db.Column(db.String(255))
    is_valid = db.Column(db.Boolean, default=True)
