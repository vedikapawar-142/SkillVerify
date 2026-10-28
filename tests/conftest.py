"""Pytest configuration and shared fixtures for Phase 1 testing.
Uses TestingConfig with an isolated in-memory SQLite database to ensure
tests never alter or delete the user's primary MySQL database.
"""
import pytest
import os
from config import TestingConfig
from app import create_app
from app.extensions import db
from app.models import User, Question
from app.services.assessment_service import seed_question_bank


@pytest.fixture(scope="session")
def app():
    """Create and configure a clean testing app instance."""
    app_instance = create_app(TestingConfig)
    with app_instance.app_context():
        db.create_all()
        seed_question_bank()
        yield app_instance
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Provide a transactional database session for tests."""
    with app.app_context():
        yield db.session
        db.session.rollback()
