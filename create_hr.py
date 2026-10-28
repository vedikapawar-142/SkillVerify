"""CLI Utility to create initial HR recruiter accounts securely.
Usage:
    python create_hr.py --name "HR Manager" --email "hr@example.com" --password "YourStrongPassword"
"""
import sys
import argparse
from app import create_app
from app.extensions import db
from app.models import User


def main():
    parser = argparse.ArgumentParser(description="Create an HR Recruiter account for AI Skill Verification Platform.")
    parser.add_argument("--name", required=True, help="Full name of the HR recruiter")
    parser.add_argument("--email", required=True, help="Email address of the HR recruiter")
    parser.add_argument("--password", required=True, help="Password for the HR account (min 6 chars)")
    
    args = parser.parse_args()

    name = args.name.strip()
    email = args.email.strip().lower()
    password = args.password

    if not name:
        print("Error: Name cannot be empty.", file=sys.stderr)
        sys.exit(1)

    if not email or "@" not in email or "." not in email:
        print("Error: Please provide a valid email address.", file=sys.stderr)
        sys.exit(1)

    if len(password) < 6:
        print("Error: Password must be at least 6 characters long.", file=sys.stderr)
        sys.exit(1)

    app = create_app()
    with app.app_context():
        existing = User.query.filter_by(email=email).first()
        if existing:
            if existing.role == "hr":
                print(f"Notice: User '{email}' already exists with role 'hr'.")
            else:
                print(f"Notice: User '{email}' exists with role '{existing.role}'. Promoting to 'hr'...")
                existing.role = "hr"
                existing.set_password(password)
                db.session.commit()
                print(f"Success: Account '{email}' updated to role 'hr'.")
            sys.exit(0)

        hr_user = User(name=name, email=email, role="hr")
        hr_user.set_password(password)
        db.session.add(hr_user)
        db.session.commit()
        print(f"Success: HR Recruiter account created for '{name}' <{email}>.")


if __name__ == "__main__":
    main()
