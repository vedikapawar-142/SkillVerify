"""Application factory for AI Skill Verification Platform (Phase 1).
Configures Flask, SQLAlchemy (MySQL through XAMPP), Flask-Login,
initializes the 80-question bank, and provides secure HR user management CLI.
"""
import os
import sys
import click
from flask import Flask
from config import Config
from .extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload and certificate folders exist
    upload_dir = app.config.get("UPLOAD_FOLDER", os.path.join(app.root_path, "..", "uploads"))
    cert_dir = app.config.get("CERTIFICATE_FOLDER", os.path.join(upload_dir, "certificates"))
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(cert_dir, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # CLI command: create-hr
    @app.cli.command("create-hr")
    @click.option("--name", prompt=True, help="Full name of the HR recruiter")
    @click.option("--email", prompt=True, help="Email address for the HR account")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password for the HR account")
    def create_hr_command(name, email, password):
        """Create a new HR recruiter account securely from command line."""
        from . import models
        email_clean = email.strip().lower()
        if not email_clean or "@" not in email_clean:
            click.echo("Error: Invalid email address.")
            return

        existing = models.User.query.filter_by(email=email_clean).first()
        if existing:
            click.echo(f"Error: An account with email '{email_clean}' already exists (Role: {existing.role}).")
            return

        hr_user = models.User(name=name.strip(), email=email_clean, role="hr")
        hr_user.set_password(password)
        db.session.add(hr_user)
        db.session.commit()
        click.echo(f"Success: HR Recruiter account created for '{name}' <{email_clean}>.")

    with app.app_context():
        from . import models  # noqa: F401

        # Test database connection and provide clear guidance if MySQL is offline
        try:
            db.create_all()

            # Schema compatibility check for Phase 1 columns on attempts table
            try:
                from sqlalchemy import text
                engine = db.engine
                with engine.connect() as conn:
                    result = conn.execute(text("SHOW COLUMNS FROM attempts LIKE 'question_ids'")).fetchone()
                    if not result:
                        conn.execute(text("ALTER TABLE attempts ADD COLUMN question_ids TEXT NULL"))
                        conn.commit()
                    pct_col = conn.execute(text("SHOW COLUMNS FROM attempts LIKE 'percentage'")).fetchone()
                    if not pct_col:
                        conn.execute(text("ALTER TABLE attempts ADD COLUMN percentage FLOAT DEFAULT 0.0"))
                        conn.commit()
                    max_col = conn.execute(text("SHOW COLUMNS FROM attempts LIKE 'max_score'")).fetchone()
                    if not max_col:
                        conn.execute(text("ALTER TABLE attempts ADD COLUMN max_score FLOAT DEFAULT 100.0"))
                        conn.commit()
            except Exception:
                # SQLite during unit tests doesn't support SHOW COLUMNS or already has it from models
                pass

        except Exception as e:
            uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
            if not app.config.get("TESTING"):
                print("=" * 70, file=sys.stderr)
                print("CRITICAL DATABASE CONNECTION ERROR:", file=sys.stderr)
                print(f"Could not connect to MySQL database via: {uri}", file=sys.stderr)
                print("Details:", e, file=sys.stderr)
                print("\nTROUBLESHOOTING INSTRUCTIONS FOR XAMPP:", file=sys.stderr)
                print("1. Open the XAMPP Control Panel on Windows.")
                print("2. Click 'Start' next to MySQL service (port 3306).")
                print("3. Ensure the database 'skillverify' exists: mysql -u root -e 'CREATE DATABASE IF NOT EXISTS skillverify;'")
                print("4. Verify credentials in your .env file match your MySQL setup.", file=sys.stderr)
                print("=" * 70, file=sys.stderr)

        # Seed the 80 calibrated MCQs into question bank
        try:
            from .services.assessment_service import seed_question_bank
            seed_question_bank()
        except Exception:
            pass

        # Seed default demo accounts if database is empty
        try:
            if not models.User.query.first():
                demo_hr = models.User(name="Demo Recruiter", email="hr@skillverify.com", role="hr")
                demo_hr.set_password("hr123456")
                demo_cand = models.User(name="Rahul Sharma", email="candidate@skillverify.com", role="candidate")
                demo_cand.set_password("cand123456")
                db.session.add_all([demo_hr, demo_cand])
                db.session.commit()
        except Exception:
            pass

    return app
