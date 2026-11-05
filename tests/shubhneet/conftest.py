"""
PayPilot AI - Test Configuration and Fixtures
Module Owner: Shubhneet
"""

import os
import tempfile
import pytest
from app import create_app
from app.config import Config
from app.database import init_db


class TestConfig(Config):
    TESTING = True
    DEBUG = False


@pytest.fixture
def app():
    """Create isolated test application with temp SQLite database."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    class RuntimeTestConfig(TestConfig):
        DATABASE_PATH = db_path

    app = create_app(RuntimeTestConfig)

    with app.app_context():
        init_db(db_path=db_path, force=True)

    yield app

    try:
        os.close(db_fd)
    except OSError:
        pass
    if os.path.exists(db_path):
        try:
            os.unlink(db_path)
        except OSError:
            pass


@pytest.fixture
def client(app):
    """Test client fixture."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Application context fixture."""
    with app.app_context():
        yield app
