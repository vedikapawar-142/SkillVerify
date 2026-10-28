"""Certificate & PDF Assessment Report Generation Service.
Utilizes:
- ReportLab for vector-rendered PDF documents
- qrcode for cryptographic / URL verification QR codes
Strictly fulfills Phase 1 specifications:
- Report contains: Platform name, Report ID, Candidate info, Language, Date, Score out of 100,
  Percentage, Correct/Incorrect counts, Skill comparison summary, Strengths/Weaknesses,
  Personalized Improvement Suggestions, and ALL 7 Questions with candidate answers,
  correct answers, and explanations.
- Certificate contains: Candidate name, Assessment language, Score out of 100, Percentage,
  Date, Unique Certificate ID, QR code linking to public verification endpoint,
  and official non-accredited disclaimer.
"""
import os
import qrcode
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from flask import current_app
from ..models import db, User, Attempt, Report, Certificate, Question, Answer


def ensure_certificate_dir() -> str:
    """Ensure directory for certificates, QR codes, and reports exists."""
    cert_dir = ""
    try:
        if current_app:
            cert_dir = current_app.config.get("CERTIFICATE_FOLDER")
    except Exception:
        pass
    if not cert_dir:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        cert_dir = os.path.join(base_dir, "uploads", "certificates")
    os.makedirs(cert_dir, exist_ok=True)
    return cert_dir


def generate_qr_code(certificate_id: str, verify_url: str) -> str:
    """Generate high-resolution PNG QR code pointing to public verification page."""
    cert_dir = ensure_certificate_dir()
    qr_filename = f"qr_{certificate_id}.png"
    qr_path = os.path.join(cert_dir, qr_filename)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="white")
    img.save(qr_path)
    return qr_path


def generate_certificate_pdf(certificate: Certificate, verify_url: str) -> str:
    """Generate a formal technical skill verification certificate in landscape PDF."""
    cert_dir = ensure_certificate_dir()
    pdf_filename = f"{certificate.certificate_id}.pdf"
    pdf_path = os.path.join(cert_dir, pdf_filename)

    # Generate QR code
    qr_path = generate_qr_code(certificate.certificate_id, verify_url)

    # Setup landscape Letter canvas
    c = canvas.Canvas(pdf_path, pagesize=landscape(letter))
    width, height = landscape(letter)

    # 1. Background fill
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # 2. Outer decorative borders
    c.setStrokeColor(colors.HexColor("#0f172a"))  # Deep Navy
    c.setLineWidth(4)
    c.rect(24, 24, width - 48, height - 48)

    c.setStrokeColor(colors.HexColor("#2563eb"))  # Royal Blue Accent
    c.setLineWidth(1.5)
    c.rect(30, 30, width - 60, height - 60)

    # Corner ornamental accents
    corner_size = 16
    c.setFillColor(colors.HexColor("#2563eb"))
    for x in [30, width - 30 - corner_size]:
        for y in [30, height - 30 - corner_size]:
            c.rect(x, y, corner_size, corner_size, fill=True, stroke=False)

    # 3. Header branding
    c.setFillColor(colors.HexColor("#1e293b"))
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(width / 2, height - 65, "AI SKILL VERIFICATION PLATFORM")

    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setLineWidth(1)
    c.line(width / 2 - 120, height - 73, width / 2 + 120, height - 73)

    # 4. Certificate Title
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 105, "CERTIFICATE OF TECHNICAL SKILL VERIFICATION")

    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height - 130, "This is an official assessment record certifying that")

    # 5. Candidate Name
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width / 2, height - 175, certificate.candidate_name)

    c.setStrokeColor(colors.HexColor("#2563eb"))
    c.setLineWidth(1.5)
    c.line(width / 2 - 160, height - 188, width / 2 + 160, height - 188)

    # 6. Assessment Details
    c.setFillColor(colors.HexColor("#334155"))
    c.setFont("Helvetica", 12)
    c.drawCentredString(
        width / 2,
        height - 215,
        f"has successfully completed the 7-Question Proportional Technical MCQ Assessment in"
    )

    c.setFillColor(colors.HexColor("#1d4ed8"))
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 245, f"{certificate.skill.upper()} PROGRAMMING")

    # 7. Score and Performance Badge
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica", 12)
    c.drawCentredString(
        width / 2,
        height - 275,
        f"Demonstrated Score: {certificate.score:.2f} / 100 ({certificate.score:.2f}%)  &bull;  Performance Category: {certificate.performance_category}"
    )

    # 8. Verification QR Code and Credentials Box
    c.drawImage(qr_path, 60, 48, width=72, height=72)

    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica", 8)
    c.drawString(140, 95, "Scan QR to verify authentic credential:")
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(140, 80, f"Certificate ID: {certificate.certificate_id}")
    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica", 8)
    c.drawString(140, 66, f"Issue Date: {certificate.issued_at.strftime('%B %d, %Y')}")
    c.drawString(140, 52, f"Verification URL: {verify_url[:50]}...")

    # 9. Signatures Block
    sig_x = width - 210
    c.setStrokeColor(colors.HexColor("#475569"))
    c.setLineWidth(1)
    c.line(sig_x, 82, sig_x + 150, 82)

    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(sig_x + 75, 68, "Platform Evaluation Engine")
    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(sig_x + 75, 54, "Automated Verification Authority")

    # 10. Mandatory Disclaimer per Phase 1 Specs
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(
        width / 2,
        34,
        "Disclaimer: This certificate verifies completion and performance on this platform's technical assessment. "
        "It does not constitute an accredited degree or guaranteed professional proficiency."
    )

    c.save()
    certificate.pdf_path = pdf_path
    certificate.qr_code_path = qr_path
    db.session.commit()
    return pdf_path


def generate_report_pdf(report: Report) -> str:
    """Generate comprehensive vector PDF Assessment Report including candidate info,
    scores, resume comparison, improvement suggestions, and all 7 evaluated questions.
    """
    cert_dir = ensure_certificate_dir()
    pdf_filename = f"skill_report_{report.id}.pdf"
    pdf_path = os.path.join(cert_dir, pdf_filename)

    attempt = report.attempt
    candidate = report.user
    questions = attempt.get_selected_questions() if attempt else []
    answers_map = {a.question_id: a for a in attempt.answers} if attempt else {}

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#0f172a")
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#64748b")
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=11,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    body_bold = ParagraphStyle(
        "BodyDarkBold",
        parent=body_style,
        fontName="Helvetica-Bold"
    )
    bullet_style = ParagraphStyle(
        "BulletText",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8
    )

    elements = []

    # Title & Metadata
    elements.append(Paragraph("AI SKILL VERIFICATION PLATFORM", title_style))
    elements.append(Paragraph(
        f"Official Candidate Technical Assessment Report &bull; "
        f"Report Ref: REP-{attempt.id if attempt else '0'}-{report.generated_at.year} &bull; "
        f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        subtitle_style
    ))
    elements.append(Spacer(1, 10))

    # Candidate Overview Table
    verified_data = report.get_verified_skills()
    score_val = attempt.final_score if attempt else 0.0
    percentage_val = attempt.percentage if attempt else 0.0
    category_val = attempt.performance_category if attempt else "N/A"
    lang_display = attempt.language_display if attempt else "Python"
    cert_status = f"Issued ({report.certificate_id})" if report.certificate_id else "Not Eligible (< 60.0%)"

    overview_data = [
        [
            Paragraph("<b>Candidate Name:</b>", body_style),
            Paragraph(candidate.name, body_style),
            Paragraph("<b>Assessment ID:</b>", body_style),
            Paragraph(f"ATT-{attempt.id if attempt else 'N/A'}", body_style)
        ],
        [
            Paragraph("<b>Candidate Email:</b>", body_style),
            Paragraph(candidate.email, body_style),
            Paragraph("<b>Assessment Language:</b>", body_style),
            Paragraph(f"<b>{lang_display}</b>", body_style)
        ],
        [
            Paragraph("<b>Final Score:</b>", body_style),
            Paragraph(f"<b>{score_val:.2f} / 100 ({percentage_val:.2f}%)</b>", body_style),
            Paragraph("<b>Performance Category:</b>", body_style),
            Paragraph(category_val, body_style)
        ],
        [
            Paragraph("<b>Questions Correct:</b>", body_style),
            Paragraph(f"{attempt.correct_count} Correct / {attempt.incorrect_count} Incorrect (out of 7)", body_style),
            Paragraph("<b>Certificate Status:</b>", body_style),
            Paragraph(cert_status, body_style)
        ]
    ]

    overview_table = Table(overview_data, colWidths=[110, 160, 115, 155])
    overview_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 10))

    # Section 1: Resume vs Assessment Comparison
    elements.append(Paragraph("1. Resume Claims vs. Assessment Performance Comparison", section_heading))
    comparison = report.get_comparison()
    claimed_skills = report.get_claimed_skills()
    comp_analysis = comparison.get("analysis", "Comparison analysis between claimed resume proficiency and verified score.")
    elements.append(Paragraph(comp_analysis, body_style))
    elements.append(Spacer(1, 5))

    claimed_str = ", ".join(claimed_skills) if claimed_skills else "None explicitly detected"
    comp_table_data = [
        [Paragraph("<b>Evaluation Metric</b>", body_style), Paragraph("<b>Claimed on Resume</b>", body_style), Paragraph("<b>Empirical Assessment Result</b>", body_style)],
        [Paragraph(f"{lang_display} Proficiency", body_style), Paragraph("Declared" if comparison.get("claimed_in_resume") else "Not Declared", body_style), Paragraph(f"Demonstrated ({score_val:.2f}%)", body_style)],
        [Paragraph("Demonstrated Status", body_style), Paragraph(comparison.get("status_label", "Evaluated"), body_style), Paragraph(category_val, body_style)],
        [Paragraph("All Extracted Resume Skills", body_style), Paragraph(claimed_str[:120] + ("..." if len(claimed_str) > 120 else ""), body_style), Paragraph("Verified in Selected Language", body_style)],
    ]
    comp_table = Table(comp_table_data, colWidths=[150, 185, 205])
    comp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(comp_table)
    elements.append(Spacer(1, 10))

    # Section 2: Improvement Suggestions
    elements.append(Paragraph("2. Evidence-Based Improvement Suggestions", section_heading))
    suggestions = report.get_improvement_suggestions()
    if suggestions:
        for s in suggestions:
            elements.append(Paragraph(f"&bull; <b>{s.get('topic', 'Topic')}:</b> {s.get('recommendation', '')}", bullet_style))
            elements.append(Spacer(1, 2))
    else:
        elements.append(Paragraph("&bull; Strong technical foundation demonstrated across all evaluated topics.", bullet_style))
    elements.append(Spacer(1, 10))

    # Section 3: Detailed Question & Answer Review (All 7 Questions)
    elements.append(Paragraph("3. Complete Question-by-Question Assessment Review (7 MCQs)", section_heading))
    
    q_table_rows = [
        [
            Paragraph("<b>#</b>", body_style),
            Paragraph("<b>Topic & Question Statement</b>", body_style),
            Paragraph("<b>Candidate Answer</b>", body_style),
            Paragraph("<b>Correct Answer & Explanation</b>", body_style),
            Paragraph("<b>Result</b>", body_style)
        ]
    ]

    for idx, q in enumerate(questions, 1):
        ans = answers_map.get(q.id)
        submitted = ans.submitted_answer if ans and ans.submitted_answer else "(No answer submitted)"
        correct = q.correct_answer or "N/A"
        is_correct = ans.is_correct if ans else False

        status_text = "<b>CORRECT</b>" if is_correct else "<b>INCORRECT</b>"
        status_color = "#16a34a" if is_correct else "#dc2626"

        q_statement_cell = f"<b>[{q.topic}]</b><br/>{q.statement}"
        explanation_cell = f"<b>{correct}</b><br/><i>{q.explanation}</i>"

        q_table_rows.append([
            Paragraph(f"Q{idx}", body_bold),
            Paragraph(q_statement_cell, body_style),
            Paragraph(submitted, body_style),
            Paragraph(explanation_cell, body_style),
            Paragraph(f"<font color='{status_color}'>{status_text}</font>", body_style)
        ])

    q_table = Table(q_table_rows, colWidths=[25, 185, 125, 150, 55])
    q_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(q_table)
    elements.append(Spacer(1, 10))

    # Disclaimer Note
    disclaimer = (
        "<b>Important Notice:</b> This assessment report is an evidence-based skill verification indicator "
        "measuring objective conceptual and practical programming comprehension through a randomized 7-question multiple-choice evaluation. "
        "It provides targeted insights for recruitment and self-improvement without claiming exhaustive software engineering accreditation."
    )
    elements.append(Paragraph(disclaimer, subtitle_style))

    doc.build(elements)
    return pdf_path


def get_or_create_certificate(attempt: Attempt, verify_base_url: str) -> Optional[Certificate]:
    """Retrieve existing certificate or generate new one if candidate meets eligibility threshold (>= 60%)."""
    if not attempt or attempt.status != "completed":
        return None

    # Check eligibility (Score >= 60.0%)
    cert_threshold = 60.0
    try:
        if current_app:
            cert_threshold = float(current_app.config.get("CERTIFICATE_THRESHOLD", 60.0))
    except Exception:
        cert_threshold = 60.0

    if (attempt.final_score or 0.0) < cert_threshold:
        return None

    existing_cert = Certificate.query.filter_by(attempt_id=attempt.id).first()
    if existing_cert:
        return existing_cert

    import uuid
    cert_id = f"CERT-{datetime.utcnow().year}-{uuid.uuid4().hex[:8].upper()}"
    verify_url = f"{verify_base_url.rstrip('/')}/certificate/verify/{cert_id}"

    user = attempt.user
    cert = Certificate(
        certificate_id=cert_id,
        attempt_id=attempt.id,
        user_id=user.id,
        candidate_name=user.name,
        skill=attempt.language_display,
        score=attempt.final_score or 0.0,
        performance_category=attempt.performance_category or "Intermediate (Competent)",
        issued_at=datetime.utcnow(),
        is_valid=True
    )
    db.session.add(cert)
    db.session.commit()

    # Generate PDF and QR code
    try:
        generate_certificate_pdf(cert, verify_url)
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Error generating certificate PDF: {e}")

    # Link into Report if exists
    report = attempt.report
    if report and not report.certificate_id:
        report.certificate_id = cert_id
        db.session.commit()

    return cert
