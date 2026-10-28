"""Assessment Service for AI Skill Verification Platform (Phase 1).
Handles:
- Question Bank Seeding (80 MCQs: 20 per language for Python, Java, C, C++)
- Randomized Selection of exactly 7 distinct questions per attempt from chosen language
- Attempt Question Persistence across page refreshes
- Server-side answer validation and anti-duplicate submission protection
- Proportional accurate scoring: Score = (Number of correct answers / 7) * 100
- Resume-to-Assessment Skill Comparison (cautious, evidence-based indicator)
- Targeted, topic-based improvement suggestions
- Automatic report and certificate generation
"""
import json
import random
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import current_app
from ..extensions import db
from ..models import User, Resume, Question, Attempt, Answer, Report, Certificate
from .question_bank_data import QUESTION_BANK_DATA
from .certificate_service import get_or_create_certificate

SUPPORTED_LANGUAGES = ["python", "java", "c", "cpp"]


def seed_question_bank():
    """Ensure all 80 calibrated MCQs exist in the MySQL database."""
    total_added = 0
    for q_data in QUESTION_BANK_DATA:
        existing = Question.query.filter_by(
            skill=q_data["skill"],
            statement=q_data["statement"]
        ).first()

        if not existing:
            q = Question(
                skill=q_data["skill"],
                type=q_data.get("type", "mcq"),
                topic=q_data.get("topic", "General"),
                difficulty=q_data.get("difficulty", 1),
                statement=q_data["statement"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation", ""),
                marks=q_data.get("marks", 100)
            )
            db.session.add(q)
            total_added += 1

    if total_added > 0:
        db.session.commit()
    return total_added


def get_or_seed_questions(skill: Optional[str] = None) -> List[Question]:
    """Retrieve questions for a given language, auto-seeding if empty."""
    query = Question.query
    if skill:
        norm_skill = skill.lower()
        query = query.filter_by(skill=norm_skill)
    questions = query.all()

    # If question bank is missing or incomplete for the requested language, re-seed
    if not questions or (skill and len(questions) < 20):
        seed_question_bank()
        query = Question.query
        if skill:
            query = query.filter_by(skill=norm_skill)
        questions = query.all()

    return questions


def start_or_resume_attempt(user_id: int, language: str) -> Attempt:
    """Start a new 7-question MCQ attempt or resume an existing in-progress attempt.
    Guarantees:
    - 7 distinct questions belonging strictly to the chosen language.
    - Persistent question selection across page refreshes.
    """
    norm_lang = language.lower()
    if norm_lang not in SUPPORTED_LANGUAGES:
        norm_lang = "python"

    # Check for existing in-progress attempt for this user and language
    existing_attempt = Attempt.query.filter_by(
        user_id=user_id,
        skill=norm_lang,
        status="in_progress"
    ).order_by(Attempt.started_at.desc()).first()

    if existing_attempt:
        # Check that it has 7 saved questions
        saved_qids = existing_attempt.get_question_ids()
        if len(saved_qids) == 7:
            return existing_attempt

    # Fetch all available questions for this language
    bank = get_or_seed_questions(norm_lang)
    if len(bank) < 7:
        raise ValueError(f"Insufficient questions in bank for language '{language}'. Required: 7, Found: {len(bank)}")

    # Randomly select exactly 7 distinct questions from the bank of 20
    selected_sample = random.sample(bank, 7)
    selected_qids = [q.id for q in selected_sample]

    attempt = Attempt(
        user_id=user_id,
        skill=norm_lang,
        status="in_progress",
        started_at=datetime.utcnow(),
        question_ids=json.dumps(selected_qids),
        total_questions=7,
        max_score=100.0,
        final_score=0.0,
        percentage=0.0,
        correct_count=0
    )
    db.session.add(attempt)
    db.session.flush()

    # Pre-create blank answer records for these 7 questions
    for q in selected_sample:
        answer = Answer(
            attempt_id=attempt.id,
            question_id=q.id,
            submitted_answer="",
            is_correct=False,
            score=0.0,
            feedback="",
            execution_engine="MCQ Evaluator"
        )
        db.session.add(answer)

    db.session.commit()
    return attempt


def determine_performance_category(score: float) -> str:
    """Categorize performance based on final score percentage."""
    if score >= 80.0:
        return "Advanced (Proficient)"
    elif score >= 60.0:
        return "Intermediate (Competent)"
    elif score >= 40.0:
        return "Developing (Basic Knowledge)"
    else:
        return "Needs Improvement"


def generate_resume_vs_assessment_comparison(
    user: User,
    language: str,
    score: float,
    percentage: float,
    correct_count: int,
    total_questions: int,
    topic_performance: Dict[str, Any]
) -> Dict[str, Any]:
    """Compare technical skills identified in resume with actual assessment performance.
    Cautious, evidence-based assessment indicator per Phase 1 requirements.
    """
    resume = user.latest_resume
    claimed_skills = resume.get_skills_list() if resume else []
    
    # Check if candidate explicitly claimed this language
    lang_display_names = {
        "python": ["python", "python3", "py"],
        "java": ["java", "core java", "j2se"],
        "c": ["c", "c language"],
        "cpp": ["c++", "cpp", "c plus plus"]
    }
    aliases = lang_display_names.get(language.lower(), [language.lower()])
    claimed_in_resume = any(s.lower() in aliases for s in claimed_skills)

    # Strengths and areas for improvement
    strengths = []
    improvement_areas = []

    for topic, stats in topic_performance.items():
        if stats.get("correct"):
            strengths.append(topic)
        else:
            improvement_areas.append(topic)

    # Difference categorization
    if claimed_in_resume:
        if percentage >= 60.0:
            status_text = "Verified Claim"
            analysis = (
                f"Candidate's resume claimed proficiency in {language.capitalize()}. "
                f"The candidate successfully demonstrated practical knowledge with an empirical score of "
                f"{percentage:.2f}% ({correct_count}/{total_questions} questions correct)."
            )
        else:
            status_text = "Performance Gap"
            analysis = (
                f"Candidate's resume listed {language.capitalize()} as a claimed skill; however, the "
                f"assessment score of {percentage:.2f}% ({correct_count}/{total_questions} questions correct) "
                f"indicates that key fundamentals require further study."
            )
    else:
        if percentage >= 60.0:
            status_text = "Undeclared Demonstrated Competence"
            analysis = (
                f"{language.capitalize()} was not explicitly highlighted as a primary skill on the candidate's "
                f"resume, but the candidate demonstrated solid competency with a score of {percentage:.2f}%."
            )
        else:
            status_text = "Exploratory Assessment"
            analysis = (
                f"Assessment in {language.capitalize()} completed as an initial baseline evaluation "
                f"with a score of {percentage:.2f}%."
            )

    return {
        "language": language.capitalize(),
        "claimed_in_resume": claimed_in_resume,
        "status_label": status_text,
        "analysis": analysis,
        "assessment_score": score,
        "percentage": percentage,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "strengths": strengths,
        "improvement_areas": improvement_areas,
        "disclaimer": (
            "Assessment-Based Indicator: This comparison is based on an empirical 7-question technical "
            "multiple-choice evaluation. It serves as an objective skill verification indicator and does not "
            "constitute an exhaustive evaluation of full-lifecycle software engineering capability."
        )
    }


def generate_improvement_suggestions(
    language: str,
    missed_topics: List[Dict[str, str]]
) -> List[Dict[str, str]]:
    """Generate actionable, language-specific learning recommendations based on missed questions."""
    suggestions = []
    seen_topics = set()

    # Topic-specific curated guidance catalog
    GUIDANCE_CATALOG = {
        # Python
        "Operators & Identity": "Review Python operator semantics, specifically the distinction between '==' (value equality) and 'is' (memory address reference identity).",
        "Data Types & Mutability": "Study mutable (list, dict, set) versus immutable (tuple, str, int) data types and their memory allocation in Python.",
        "Lists & Slicing": "Practice Python sequence slicing syntax [start:stop:step] and negative index positioning.",
        "Loops & Control Flow": "Revise Python loop construct rules, including the execution timing of loop 'else' blocks and 'break' statements.",
        "Functions & Default Arguments": "Be mindful of mutable default arguments in function definitions; use None as a default sentinel to avoid shared mutation bugs.",
        "Dictionaries & Lookup": "Utilize `dict.get(key, default)` for resilient lookups to avoid unhandled KeyErrors in production code.",
        "List Comprehensions": "Practice compact iterable transformations and conditionals with list, dict, and set comprehensions.",
        "Exceptions & Handling": "Study the complete `try-except-else-finally` lifecycle and custom exception hierarchies.",
        "Functions & Unpacking": "Revise positional (*args) and keyword (**kwargs) argument packing and tuple/dict unpacking.",
        "Variable Scope & LEGB": "Understand Python's LEGB (Local, Enclosing, Global, Built-in) lookup rules and the `nonlocal` and `global` keywords.",
        "String Operations": "Practice string formatting methods, join/split operations, and immutable string performance.",
        "Context Managers": "Familiarize yourself with Python context managers (`with` statement) and implementing `__enter__` and `__exit__`.",
        "Generators & Yield": "Explore iterator protocols and memory-efficient stream processing with `yield` and generator expressions.",
        "Lambda & Built-ins": "Practice functional programming helpers such as `map()`, `filter()`, `reduce()`, and lambda expressions.",
        "Object-Oriented Programming": "Revise object-oriented principles, dunder methods (`__init__`, `__str__`, `__repr__`), and method resolution order.",
        "Class vs Static Methods": "Understand the differences between regular instance methods (`self`), `@classmethod` (`cls`), and `@staticmethod`.",
        "Sets & Uniqueness": "Utilize mathematical set operations (union, intersection, difference) for O(1) membership testing and deduplication.",
        "Debugging & Exceptions": "Strengthen diagnostic skills for standard runtime exceptions: IndexError, TypeError, and AttributeError.",
        "Copies: Shallow vs Deep": "Understand when to use shallow copy (`copy.copy`) versus deep copy (`copy.deepcopy`) on nested structures.",
        "Collections & Counting": "Explore specialized data structures in the standard library `collections` module like `Counter`, `defaultdict`, and `deque`.",

        # Java
        "String Immutability & Pool": "Revise Java's String Constant Pool and always use `.equals()` rather than `==` for String content comparison.",
        "Primitive Types & Autoboxing": "Understand Java primitive types, their memory footprints on the stack, and wrapper class autoboxing nuances.",
        "Access Modifiers": "Review Java's 4 access levels: `private`, default (package-private), `protected`, and `public`.",
        "The final Keyword": "Understand the constraints of `final` applied to variables (constants), methods (cannot override), and classes (cannot inherit).",
        "Inheritance & Super": "Revise constructor chaining in Java inheritance; remember `super()` must be the very first statement in a subclass constructor.",
        "Method Overloading vs Overriding": "Distinguish between compile-time overloading (different parameters) and runtime overriding (exact signature with dynamic dispatch).",
        "Interfaces & Default Methods": "Study modern Java interfaces, abstract method contracts, and `default` method backward compatibility.",
        "Exception Handling": "Understand Checked exceptions (requiring throws/catch) versus Unchecked RuntimeExceptions.",
        "Collections: List Types": "Analyze algorithmic trade-offs between contiguous `ArrayList` (O(1) access) and linked `LinkedList` (O(1) insert/delete at ends).",
        "Collections: Map Contract": "Master the contract between `equals()` and `hashCode()` for reliable hash bucket resolution in `HashMap` and `HashSet`.",
        "StringBuilder vs String": "Use `StringBuilder` to avoid intermediate String allocation in loops and intensive text processing.",
        "The static Keyword": "Understand class-level state and why `static` methods cannot directly access `this` or non-static members.",
        "Polymorphism & Binding": "Deepen understanding of dynamic method dispatch and runtime polymorphism in Java.",
        "Memory Architecture": "Review JVM runtime data areas: Stack frames for local primitives vs Heap for dynamic objects.",

        # C
        "Operators: Increment": "Clarify post-increment (`a++`) vs pre-increment (`++a`) operation order in expressions.",
        "Data Types & Sizeof": "Remember that `sizeof` evaluates size in bytes at compile time, and `sizeof(char)` is always 1.",
        "Pointers: Dereference": "Practice memory address referencing with `&` and value dereferencing with `*`.",
        "Pointer Arithmetic": "Remember that pointer arithmetic steps by the byte size of the pointed-to type, not raw 1-byte increments.",
        "Strings & Null Terminator": "Ensure character arrays always allocate space for the null terminator byte `\\0`.",
        "String Functions": "Familiarize with `<string.h>` functions (`strlen`, `strcpy`, `strcmp`) and prefer bounded versions (`strncpy`).",
        "Dynamic Memory: Malloc vs Calloc": "Remember that `malloc()` does not zero memory; use `calloc()` when initialized zero bytes are required.",
        "Memory Leaks & Free": "Always pair dynamic allocations (`malloc`/`calloc`) with `free()` and nullify pointers to avoid dangling pointer bugs.",
        "Storage Classes": "Study the persistence of local `static` variables and linkage of `extern` declarations.",
        "Structures & Member Access": "Use dot `.` with struct values and arrow `->` with struct pointers.",
        "Bitwise Operators": "Practice bit masking, shifts (`<<`, `>>`), and bitwise boolean operations (`&`, `|`, `^`).",

        # C++
        "References vs Pointers": "Use references for safe, non-null aliases and pointers when reseating or nullability is required.",
        "Constructors & Destructors": "Understand object lifecycle, constructor initialization lists, and LIFO destruction order on the stack.",
        "Virtual Functions & Polymorphism": "Declare polymorphic base methods as `virtual` to enable vtable runtime dispatch.",
        "Abstract Classes & Pure Virtual": "Declare pure virtual functions (`= 0`) to enforce interface contracts in abstract base classes.",
        "Virtual Destructors": "Always make base class destructors `virtual` to prevent memory leaks when deleting derived objects via base pointers.",
        "STL: Vector Operations": "Practice standard `std::vector` idioms: `push_back`, `emplace_back`, capacity reservation, and size.",
        "STL: Map vs Unordered Map": "Understand the difference between ordered `std::map` (Red-Black tree, O(log n)) and `std::unordered_map` (Hash table, O(1)).",
        "Modern C++: unique_ptr": "Adopt smart pointers: use `std::unique_ptr` for exclusive ownership and eliminate manual `delete` calls.",
        "RAII Idiom": "Apply Resource Acquisition Is Initialization (RAII) to manage OS handles, sockets, and memory automatically."
    }

    for item in missed_topics:
        t = item.get("topic", "")
        if t and t not in seen_topics:
            seen_topics.add(t)
            advice = GUIDANCE_CATALOG.get(
                t,
                f"Review fundamental principles of {t} in {language.capitalize()} and practice with targeted coding exercises."
            )
            suggestions.append({
                "topic": t,
                "recommendation": advice
            })

    # If candidate scored 100% or had very few mistakes, provide an advanced suggestion
    if not suggestions:
        suggestions.append({
            "topic": f"Advanced {language.capitalize()} Mastery",
            "recommendation": (
                f"Demonstrated strong mastery of {language.capitalize()} core fundamentals! Continue advancing to "
                f"concurrency, design patterns, algorithmic optimization, and system architecture."
            )
        })

    return suggestions


def evaluate_assessment(
    attempt_id: int,
    form_data: Dict[str, str],
    request_base_url: str = ""
) -> Attempt:
    """Evaluate candidate answers, calculate score out of 100, and generate reports.
    Requirements satisfied:
    - 7 distinct questions scored proportionally: Score = (correct / 7) * 100
    - Prevents duplicate submission or score modification
    - Verifies question ownership
    - Saves answers, score, and reports in MySQL
    - Generates QR-verified certificate when eligible (score >= 60%)
    """
    attempt = db.session.get(Attempt, attempt_id)
    if not attempt:
        raise ValueError(f"Attempt #{attempt_id} not found.")

    # Guard: prevent accidental re-submission and duplicate calculation
    if attempt.status == "completed":
        return attempt

    # Retrieve the exact 7 questions saved for this attempt
    questions = attempt.get_selected_questions()
    if not questions or len(questions) != 7:
        raise ValueError(f"Invalid question set for attempt #{attempt_id}.")

    correct_count = 0
    topic_performance: Dict[str, Any] = {}
    missed_topics: List[Dict[str, str]] = []

    for q in questions:
        q_id_str = str(q.id)
        # Form field key: q_<id>
        submitted_val = form_data.get(f"q_{q_id_str}", "").strip()

        # Check correctness against question's correct answer
        is_correct = bool(submitted_val and (submitted_val.strip() == q.correct_answer.strip()))

        question_score = (100.0 / 7.0) if is_correct else 0.0
        if is_correct:
            correct_count += 1
            feedback = f"Correct! {q.explanation}"
        else:
            feedback = f"Incorrect. Correct answer: {q.correct_answer}. {q.explanation}"
            missed_topics.append({
                "question_id": q.id,
                "topic": q.topic or "General",
                "statement": q.statement
            })

        topic_name = q.topic or "General"
        if topic_name not in topic_performance:
            topic_performance[topic_name] = {
                "correct": is_correct,
                "marks_obtained": question_score,
                "marks_total": (100.0 / 7.0),
                "statement": q.statement
            }
        else:
            topic_performance[topic_name]["marks_total"] += (100.0 / 7.0)
            if is_correct:
                topic_performance[topic_name]["marks_obtained"] += question_score
                topic_performance[topic_name]["correct"] = True

        # Find or create Answer row for this question
        ans = Answer.query.filter_by(attempt_id=attempt.id, question_id=q.id).first()
        if not ans:
            ans = Answer(attempt_id=attempt.id, question_id=q.id)
            db.session.add(ans)

        ans.submitted_answer = submitted_val
        ans.is_correct = is_correct
        ans.score = question_score
        ans.feedback = feedback
        ans.execution_engine = "MCQ Objective Evaluator"

    # Calculate exact final score: (correct / 7) * 100
    # Store exact unrounded float; display is rounded to two decimal places
    raw_score = (correct_count / 7.0) * 100.0
    display_score = round(raw_score, 2)

    attempt.correct_count = correct_count
    attempt.total_questions = 7
    attempt.final_score = display_score
    attempt.percentage = display_score
    attempt.max_score = 100.0
    attempt.completed_at = datetime.utcnow()
    attempt.status = "completed"
    attempt.performance_category = determine_performance_category(raw_score)

    # Generate Resume-to-Assessment Skill Comparison
    user = attempt.user
    comparison_data = generate_resume_vs_assessment_comparison(
        user=user,
        language=attempt.skill,
        score=display_score,
        percentage=display_score,
        correct_count=correct_count,
        total_questions=7,
        topic_performance=topic_performance
    )

    # Generate Targeted Improvement Suggestions
    suggestions = generate_improvement_suggestions(
        language=attempt.skill,
        missed_topics=missed_topics
    )

    # Create or update official Report record in MySQL
    report = Report.query.filter_by(attempt_id=attempt.id).first()
    if not report:
        report = Report(attempt_id=attempt.id, user_id=user.id)
        db.session.add(report)

    claimed_skills = user.latest_resume.get_skills_list() if user.latest_resume else []
    report.verified_skills = json.dumps({
        "language": attempt.skill,
        "score": display_score,
        "percentage": display_score,
        "correct_count": correct_count,
        "total_questions": 7,
        "category": attempt.performance_category
    })
    report.claimed_skills = json.dumps(claimed_skills)
    report.comparison_summary = json.dumps(comparison_data)
    report.strengths_weaknesses = json.dumps(topic_performance)
    report.improvement_suggestions = json.dumps(suggestions)
    report.generated_at = datetime.utcnow()

    db.session.commit()

    # Certificate Generation Workflow (Threshold: 60.0%)
    cert_threshold = 60.0
    try:
        cert_threshold = float(current_app.config.get("CERTIFICATE_THRESHOLD", 60.0))
    except Exception:
        cert_threshold = 60.0

    if display_score >= cert_threshold:
        try:
            cert = get_or_create_certificate(attempt, request_base_url)
            if cert and not report.certificate_id:
                report.certificate_id = cert.certificate_id
                db.session.commit()
        except Exception as e:
            if current_app:
                current_app.logger.warning(f"Certificate generation error: {e}")

    return attempt
