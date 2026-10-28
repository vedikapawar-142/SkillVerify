"""Main application routes for candidates, technical assessments, comparisons,
reports, certificates, and HR recruitment management.
Strictly implements Phase 1 specifications:
- 4 Supported Languages: Python, Java, C, C++
- Randomized 7-question MCQ assessment from 20-question bank
- Question persistence across page refreshes
- Proportional scoring: Score = (correct / 7) * 100
- Dedicated post-submission answer review showing questions, selected answers, correct answers, explanations
- Resume-to-assessment skill comparison and targeted improvement suggestions
- Downloadable ReportLab PDF reports and QR-verified certificates (threshold >= 60%)
- Protected HR portal with search, filtering by language/score/status, and candidate drill-down
"""
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import (
    Blueprint, render_template, request, redirect, 
    url_for, flash, current_app, abort, send_file, jsonify
)
from flask_login import login_required, current_user
from ..extensions import db
from ..models import User, Resume, JobRole, Question, Attempt, Answer, Report, Certificate
from .auth import candidate_required, hr_required
from ..services.resume_parser import (
    validate_resume_file, extract_resume_text, analyze_resume_text
)
from ..services.llm import analyze_resume_with_gemini
from ..services.assessment_service import (
    get_or_seed_questions, start_or_resume_attempt, evaluate_assessment,
    SUPPORTED_LANGUAGES
)
from ..services.certificate_service import (
    get_or_create_certificate, generate_certificate_pdf, generate_report_pdf
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """Platform landing page."""
    if current_user.is_authenticated:
        if current_user.role in ("hr", "admin"):
            return redirect(url_for("main.hr_dashboard"))
        return redirect(url_for("main.dashboard"))
    return render_template("index.html")


@main_bp.route("/dashboard")
@candidate_required
def dashboard():
    """Candidate dashboard showing resume status, extracted skills, language selection,
    assessment history, latest scores, and verified certificates.
    """
    latest_resume = current_user.latest_resume
    parsed_data = latest_resume.get_parsed_data() if latest_resume else {}
    claimed_skills = latest_resume.get_skills_list() if latest_resume else []
    categorized_skills = parsed_data.get("categorized_skills", {})
    
    attempts = Attempt.query.filter_by(user_id=current_user.id).order_by(Attempt.started_at.desc()).all()
    completed_attempts = [a for a in attempts if a.status == "completed"]
    latest_completed = completed_attempts[0] if completed_attempts else None
    latest_report = latest_completed.report if latest_completed else None
    latest_certificate = latest_completed.certificate if latest_completed else None
    
    comparison_summary = latest_report.get_comparison() if latest_report else {}
    suggestions = latest_report.get_improvement_suggestions() if latest_report else []

    return render_template(
        "dashboard.html",
        user=current_user,
        resume=latest_resume,
        parsed_data=parsed_data,
        claimed_skills=claimed_skills,
        categorized_skills=categorized_skills,
        attempts=attempts,
        completed_attempts=completed_attempts,
        latest_attempt=latest_completed,
        latest_report=latest_report,
        latest_certificate=latest_certificate,
        comparison_summary=comparison_summary,
        suggestions=suggestions
    )


@main_bp.route("/resume/upload", methods=["GET", "POST"])
@candidate_required
def upload_resume():
    """Upload and process candidate resume in PDF or DOCX format."""
    if request.method == "POST":
        if "resume_file" not in request.files:
            flash("No file was selected for upload.", "danger")
            return redirect(request.url)
            
        file = request.files["resume_file"]
        if file.filename == "":
            flash("Please choose a valid resume file.", "danger")
            return redirect(request.url)

        # Secure filename and unique storage path
        original_name = secure_filename(file.filename)
        safe_name = f"user_{current_user.id}_{uuid.uuid4().hex[:8]}_{original_name}"
        upload_folder = current_app.config.get("UPLOAD_FOLDER", os.path.join(os.getcwd(), "uploads"))
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, safe_name)
        
        try:
            file.save(file_path)

            # Validate file existence, size, extension, and magic header bytes
            is_valid, validation_msg = validate_resume_file(
                file_path,
                max_size_bytes=current_app.config.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024)
            )
            if not is_valid:
                if os.path.exists(file_path):
                    os.remove(file_path)
                flash(validation_msg, "danger")
                return redirect(request.url)

            # Extract readable text using PyPDF2 / python-docx
            raw_text = extract_resume_text(file_path)

            # AI Resume Analysis (Gemini if key is configured, or local rule-based fallback)
            analysis = analyze_resume_with_gemini(raw_text)
            claimed_skills = analysis.get("technical_skills", [])

            # Check if candidate already has a resume record; update or create
            resume = Resume.query.filter_by(user_id=current_user.id).first()
            if not resume:
                resume = Resume(user_id=current_user.id)
                db.session.add(resume)

            resume.filename = original_name
            resume.file_path = file_path
            resume.raw_text = raw_text
            resume.extracted_skills = json.dumps(claimed_skills)
            resume.parsed_data = json.dumps(analysis)
            resume.status = "processed"
            resume.uploaded_at = datetime.utcnow()
            
            db.session.commit()
            flash(
                f"Resume uploaded and analyzed successfully ({analysis.get('engine', 'Analyzer')})! "
                "Please review your extracted claimed skills below.",
                "success"
            )
            return redirect(url_for("main.review_resume"))

        except Exception as e:
            db.session.rollback()
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass
            flash(f"Resume validation failed: {str(e)}", "danger")
            return redirect(request.url)

    return render_template("resume_upload.html", resume=current_user.latest_resume)


@main_bp.route("/resume/review", methods=["GET", "POST"])
@candidate_required
def review_resume():
    """Allow candidate to inspect, confirm, or refine claimed technical skills."""
    resume = current_user.latest_resume
    if not resume:
        flash("Please upload a resume first.", "warning")
        return redirect(url_for("main.upload_resume"))

    parsed_data = resume.get_parsed_data()
    claimed_skills = resume.get_skills_list()

    if request.method == "POST":
        skills_input = request.form.get("skills_list", "")
        edited_skills = [s.strip() for s in skills_input.replace("\n", ",").split(",") if s.strip()]
        
        seen = set()
        unique_skills = []
        for s in edited_skills:
            if s.lower() not in seen:
                seen.add(s.lower())
                unique_skills.append(s)

        resume.extracted_skills = json.dumps(unique_skills)
        resume.status = "reviewed"
        db.session.commit()

        flash("Claimed skills confirmed! You can now select your programming language and take the assessment.", "success")
        return redirect(url_for("main.select_language"))

    return render_template(
        "resume_review.html",
        resume=resume,
        parsed_data=parsed_data,
        claimed_skills=claimed_skills
    )


@main_bp.route("/resume/download/<int:resume_id>")
@login_required
def download_resume(resume_id: int):
    """Protected resume file download (strictly accessible by owner candidate or HR)."""
    resume = db.get_or_404(Resume, resume_id)
    if current_user.role == "candidate" and resume.user_id != current_user.id:
        abort(403)

    if not resume.file_path or not os.path.exists(resume.file_path):
        flash("Resume file is not available on server storage.", "warning")
        return redirect(url_for("main.dashboard"))

    return send_file(
        resume.file_path,
        as_attachment=True,
        download_name=resume.filename or f"resume_{resume.id}.pdf"
    )


@main_bp.route("/assessment/select-language")
@candidate_required
def select_language():
    """Language selection portal: Python, Java, C, or C++ with pre-test briefing."""
    resume = current_user.latest_resume
    claimed_skills = resume.get_skills_list() if resume else []
    
    # Check for active in-progress attempts
    active_attempts = Attempt.query.filter_by(
        user_id=current_user.id,
        status="in_progress"
    ).all()
    active_by_lang = {a.skill.lower(): a.id for a in active_attempts}

    return render_template(
        "assessment_instructions.html",
        resume=resume,
        claimed_skills=claimed_skills,
        active_by_lang=active_by_lang,
        supported_languages=SUPPORTED_LANGUAGES
    )


@main_bp.route("/assessment/instructions")
@candidate_required
def assessment_instructions():
    """Alias for select_language for backwards compatibility."""
    return redirect(url_for("main.select_language"))


@main_bp.route("/assessment/start/<language>", methods=["GET", "POST"])
@candidate_required
def start_assessment_route(language: str):
    """Initiate a 7-question MCQ attempt for the chosen language or resume in-progress attempt."""
    norm_lang = language.lower()
    if norm_lang not in SUPPORTED_LANGUAGES:
        flash(f"Language '{language}' is not supported. Please choose Python, Java, C, or C++.", "warning")
        return redirect(url_for("main.select_language"))

    try:
        attempt = start_or_resume_attempt(current_user.id, norm_lang)
        return redirect(url_for("main.take_assessment", attempt_id=attempt.id))
    except Exception as e:
        flash(f"Error starting assessment: {str(e)}", "danger")
        return redirect(url_for("main.select_language"))


@main_bp.route("/assessment/take", methods=["GET", "POST"])
@candidate_required
def take_assessment_default():
    """Redirect to active attempt or prompt language selection."""
    active = Attempt.query.filter_by(user_id=current_user.id, status="in_progress").order_by(Attempt.started_at.desc()).first()
    if active:
        return redirect(url_for("main.take_assessment", attempt_id=active.id))
    return redirect(url_for("main.select_language"))


@main_bp.route("/assessment/take/<int:attempt_id>", methods=["GET", "POST"])
@candidate_required
def take_assessment(attempt_id: int):
    """Interactive 7-question MCQ assessment interface.
    Features:
    - Exactly 7 distinct questions from chosen language
    - Question persistence across page refreshes
    - Question navigation (1 to 7) with answered status indicators
    - Allows changing answers before final submission
    - Submission confirmation modal
    - Proportional score calculation: Score = (correct / 7) * 100
    - Immediate post-submission redirect to dedicated answer review page
    """
    attempt = db.get_or_404(Attempt, attempt_id)
    if attempt.user_id != current_user.id:
        abort(403)

    # Prevent re-taking completed assessment
    if attempt.status == "completed":
        flash("This assessment attempt has already been submitted and finalized.", "info")
        return redirect(url_for("main.assessment_result", attempt_id=attempt.id))

    # Retrieve the exact 7 questions saved for this attempt
    questions = attempt.get_selected_questions()
    if len(questions) != 7:
        flash("Assessment question configuration error. Please start a new attempt.", "danger")
        return redirect(url_for("main.select_language"))

    # Map existing answers
    existing_answers = {a.question_id: a.submitted_answer for a in attempt.answers}

    if request.method == "POST":
        try:
            evaluate_assessment(
                attempt_id=attempt.id,
                form_data=request.form,
                request_base_url=request.host_url
            )
            flash(
                f"Assessment submitted successfully! Final Score: {attempt.final_score:.2f} / 100 ({attempt.percentage:.2f}%) "
                f"[{attempt.performance_category}]. Review your answers and explanations below.",
                "success"
            )
            return redirect(url_for("main.assessment_result", attempt_id=attempt.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error submitting assessment: {str(e)}", "danger")

    return render_template(
        "assessment_take.html",
        attempt=attempt,
        questions=questions,
        existing_answers=existing_answers,
        total_questions=7
    )


@main_bp.route("/assessment/result/<int:attempt_id>")
@login_required
def assessment_result(attempt_id: int):
    """Dedicated post-submission Assessment Results and Answer Review page.
    Displays:
    - Selected language, date, and completion status
    - Final score out of 100 and percentage (e.g. 85.71%)
    - Correct and incorrect counts (e.g. 6 Correct, 1 Incorrect)
    - All 7 questions with candidate's submitted answer, correct answer, and explanation
    - Visual indicators for correct / incorrect
    - Resume-to-assessment skill comparison
    - Targeted improvement suggestions
    - Download links for ReportLab PDF report and verifiable Certificate
    """
    attempt = db.get_or_404(Attempt, attempt_id)
    if current_user.role == "candidate" and attempt.user_id != current_user.id:
        abort(403)

    questions = attempt.get_selected_questions()
    answers_map = {a.question_id: a for a in attempt.answers}

    report = attempt.report
    comparison = report.get_comparison() if report else {}
    strengths_weaknesses = report.get_strengths_weaknesses() if report else {}
    suggestions = report.get_improvement_suggestions() if report else []
    certificate = attempt.certificate

    return render_template(
        "assessment_result.html",
        attempt=attempt,
        questions=questions,
        answers_map=answers_map,
        report=report,
        comparison=comparison,
        strengths=strengths_weaknesses,
        suggestions=suggestions,
        certificate=certificate
    )


@main_bp.route("/report/<int:report_id>")
@login_required
def view_report(report_id: int):
    """Web view of the skill verification report."""
    report = db.get_or_404(Report, report_id)
    attempt = report.attempt
    candidate = report.user

    if current_user.role == "candidate" and report.user_id != current_user.id:
        abort(403)

    questions = attempt.get_selected_questions() if attempt else []
    answers_map = {a.question_id: a for a in attempt.answers} if attempt else {}

    verified_skills = report.get_verified_skills()
    claimed_skills = report.get_claimed_skills()
    comparison = report.get_comparison()
    strengths_weaknesses = report.get_strengths_weaknesses()
    suggestions = report.get_improvement_suggestions()
    resume = candidate.latest_resume
    certificate = attempt.certificate if attempt else None

    return render_template(
        "report_detail.html",
        report=report,
        attempt=attempt,
        candidate=candidate,
        questions=questions,
        answers_map=answers_map,
        verified_skills=verified_skills,
        claimed_skills=claimed_skills,
        comparison=comparison,
        strengths=strengths_weaknesses,
        suggestions=suggestions,
        resume=resume,
        certificate=certificate
    )


@main_bp.route("/report/<int:report_id>/pdf")
@login_required
def download_report_pdf(report_id: int):
    """Generate and download vector PDF assessment report via ReportLab."""
    report = db.get_or_404(Report, report_id)
    if current_user.role == "candidate" and report.user_id != current_user.id:
        abort(403)

    try:
        pdf_path = generate_report_pdf(report)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"skill_report_attempt_{report.attempt_id}.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        flash(f"Error generating PDF report: {e}", "danger")
        return redirect(url_for("main.assessment_result", attempt_id=report.attempt_id))


@main_bp.route("/certificate/<certificate_id>/download")
@login_required
def download_certificate(certificate_id: str):
    """Download verifiable PDF skill verification certificate."""
    cert = Certificate.query.filter_by(certificate_id=certificate_id).first_or_404()
    if current_user.role == "candidate" and cert.user_id != current_user.id:
        abort(403)

    if not cert.pdf_path or not os.path.exists(cert.pdf_path):
        verify_url = url_for("main.verify_certificate", certificate_id=cert.certificate_id, _external=True)
        generate_certificate_pdf(cert, verify_url)

    return send_file(
        cert.pdf_path,
        as_attachment=True,
        download_name=f"{cert.certificate_id}.pdf",
        mimetype="application/pdf"
    )


@main_bp.route("/certificate/verify/<certificate_id>")
def verify_certificate(certificate_id: str):
    """Public certificate verification endpoint (QR code target).
    Checks database validity and displays verified status without exposing sensitive candidate details.
    """
    cert = Certificate.query.filter_by(certificate_id=certificate_id).first()
    return render_template("certificate_verify.html", certificate=cert, cert_id=certificate_id)


@main_bp.route("/hr/dashboard")
@hr_required
def hr_dashboard():
    """HR Recruiter portal with real candidate records, search, and multi-parameter filtering.
    Filters:
    - Search by candidate name or email
    - Filter by programming language (Python, Java, C, C++, or All)
    - Filter by score range (80-100, 60-79, 40-59, <40, or All)
    - Filter by assessment status (Completed, Pending, All)
    - Sort by recent, highest score, lowest score, name
    """
    search_query = request.args.get("q", "").strip().lower()
    lang_filter = request.args.get("lang", "all").strip().lower()
    score_filter = request.args.get("score_range", "all").strip()
    status_filter = request.args.get("status", "all").strip()
    sort_by = request.args.get("sort", "recent").strip()

    # Query all candidates
    candidates_query = User.query.filter_by(role="candidate")

    if search_query:
        candidates_query = candidates_query.filter(
            (User.name.ilike(f"%{search_query}%")) | (User.email.ilike(f"%{search_query}%"))
        )

    all_candidates = candidates_query.all()
    candidate_data = []
    total_assessments_completed = 0
    total_scores = 0.0

    for cand in all_candidates:
        resume = cand.latest_resume
        skills = resume.get_skills_list() if resume else []
        attempts = Attempt.query.filter_by(user_id=cand.id).order_by(Attempt.started_at.desc()).all()
        completed = [a for a in attempts if a.status == "completed"]
        latest_attempt = completed[0] if completed else (attempts[0] if attempts else None)

        status = "No Resume"
        if resume:
            status = "Resume Uploaded"
        if completed:
            status = "Assessment Completed"
            total_assessments_completed += 1
            total_scores += (latest_attempt.final_score or 0.0)

        # Apply status filter
        if status_filter == "completed" and status != "Assessment Completed":
            continue
        elif status_filter == "pending" and status == "Assessment Completed":
            continue

        # Apply language filter
        attempt_lang = (latest_attempt.skill or "").lower() if latest_attempt else ""
        if lang_filter != "all" and attempt_lang != lang_filter:
            continue

        # Apply score range filter
        score = latest_attempt.final_score if (latest_attempt and latest_attempt.status == "completed") else -1.0
        if score_filter == "80_100" and not (score >= 80.0):
            continue
        elif score_filter == "60_79" and not (60.0 <= score < 80.0):
            continue
        elif score_filter == "40_59" and not (40.0 <= score < 60.0):
            continue
        elif score_filter == "below_40" and not (0.0 <= score < 40.0):
            continue

        candidate_data.append({
            "user": cand,
            "resume": resume,
            "skills": skills,
            "status": status,
            "latest_attempt": latest_attempt,
            "score": score,
            "language": latest_attempt.language_display if latest_attempt else "N/A",
            "certificate": latest_attempt.certificate if latest_attempt else None,
            "report": latest_attempt.report if latest_attempt else None
        })

    # Sorting
    if sort_by == "highest":
        candidate_data.sort(key=lambda x: x["score"], reverse=True)
    elif sort_by == "lowest":
        candidate_data.sort(key=lambda x: x["score"])
    elif sort_by == "name":
        candidate_data.sort(key=lambda x: x["user"].name.lower())
    else:  # recent
        candidate_data.sort(key=lambda x: x["user"].created_at or datetime.min, reverse=True)

    avg_score = round(total_scores / total_assessments_completed, 2) if total_assessments_completed > 0 else 0.0

    return render_template(
        "hr_dashboard.html",
        candidates=candidate_data,
        total_candidates=len(all_candidates),
        completed_count=total_assessments_completed,
        pending_count=len(all_candidates) - total_assessments_completed,
        avg_score=avg_score,
        search_query=search_query,
        lang_filter=lang_filter,
        score_filter=score_filter,
        status_filter=status_filter,
        sort_by=sort_by
    )


@main_bp.route("/hr/candidate/<int:user_id>")
@hr_required
def hr_candidate_detail(user_id: int):
    """Detailed view of a candidate record for HR."""
    candidate = db.get_or_404(User, user_id)
    if candidate.role != "candidate":
        abort(404)

    resume = candidate.latest_resume
    parsed_resume = resume.get_parsed_data() if resume else {}
    claimed_skills = resume.get_skills_list() if resume else []
    
    attempts = Attempt.query.filter_by(user_id=candidate.id).order_by(Attempt.started_at.desc()).all()
    completed_attempts = [a for a in attempts if a.status == "completed"]
    latest_attempt = completed_attempts[0] if completed_attempts else None
    latest_report = latest_attempt.report if latest_attempt else None
    comparison = latest_report.get_comparison() if latest_report else {}
    suggestions = latest_report.get_improvement_suggestions() if latest_report else []
    certificate = latest_attempt.certificate if latest_attempt else None

    return render_template(
        "hr_candidate_detail.html",
        candidate=candidate,
        resume=resume,
        parsed_resume=parsed_resume,
        claimed_skills=claimed_skills,
        attempts=attempts,
        completed_attempts=completed_attempts,
        latest_attempt=latest_attempt,
        latest_report=latest_report,
        comparison=comparison,
        suggestions=suggestions,
        certificate=certificate
    )


@main_bp.route("/profile")
@login_required
def profile():
    """User account profile."""
    return render_template("profile.html", user=current_user)
