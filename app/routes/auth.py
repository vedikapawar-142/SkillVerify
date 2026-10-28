"""Authentication routes and role-based access control decorators.
Implements Phase 1 security requirements:
- Secure password hashing via Werkzeug
- Server-side role authorization
- Public registration strictly restricted to candidate role (no role spoofing)
- Dedicated HR recruiter login portal (/hr/login)
- Duplicate email validation and input sanitation
- Session management with clear flash messages
"""
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db
from ..models import User

auth_bp = Blueprint("auth", __name__)


def candidate_required(f):
    """Decorator to restrict access to candidates only."""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role != "candidate":
            flash("This page is reserved for candidates.", "warning")
            if current_user.role in ("hr", "admin"):
                return redirect(url_for("main.hr_dashboard"))
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated_function


def hr_required(f):
    """Decorator to restrict access to HR recruiters and admins only.
    Prevents candidates from accessing HR endpoints even if URL is typed directly.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.role not in ("hr", "admin"):
            flash("Access denied. Authorized HR recruiter credentials required.", "danger")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Candidate self-registration. Public registration strictly enforces role='candidate'."""
    if current_user.is_authenticated:
        if current_user.role in ("hr", "admin"):
            return redirect(url_for("main.hr_dashboard"))
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Strict security: public registration cannot create HR accounts
        role = "candidate"

        if not name:
            flash("Full name is required.", "danger")
        elif not email or "@" not in email or "." not in email:
            flash("A valid email address is required.", "danger")
        elif len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("An account with this email address already exists. Please log in.", "danger")
        else:
            user = User(name=name, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Candidate registration successful! Please log in with your credentials.", "success")
            return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/hr/login", methods=["GET", "POST"])
def hr_login():
    """Protected HR Recruiter login portal."""
    if current_user.is_authenticated:
        if current_user.role in ("hr", "admin"):
            return redirect(url_for("main.hr_dashboard"))
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        if not email or not password:
            flash("Please provide both email and password.", "danger")
            return render_template("login.html", hr_portal=True)

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.role not in ("hr", "admin"):
                flash("Access denied. These credentials do not have HR privileges.", "danger")
                return render_template("login.html", hr_portal=True)
            login_user(user, remember=remember)
            flash(f"Welcome to the HR Recruitment Portal, {user.name}!", "success")
            return redirect(url_for("main.hr_dashboard"))

        flash("Invalid HR credentials. Please verify your email and password.", "danger")

    return render_template("login.html", hr_portal=True)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Standard user login (automatically redirects based on role)."""
    if current_user.is_authenticated:
        if current_user.role in ("hr", "admin"):
            return redirect(url_for("main.hr_dashboard"))
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html", hr_portal=False)

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.name}!", "success")
            if user.role in ("hr", "admin"):
                return redirect(url_for("main.hr_dashboard"))
            return redirect(url_for("main.dashboard"))

        flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html", hr_portal=False)


@auth_bp.route("/logout")
@login_required
def logout():
    """Secure logout."""
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("main.index"))
