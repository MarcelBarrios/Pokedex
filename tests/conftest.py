# tests/conftest.py
from models import User, Pokemon  # Assuming models.py is in the project_root
from config import TestingConfig
from app import create_app, db  # Assuming app.py is in the project_root
import pytest
import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for the entire test session."""
    _app = create_app(config_name='testing')

    with _app.app_context():
        db.create_all()  # Create all tables

        # Seed initial data only if it doesn't exist
        # (safer if tests might run in parallel or if fixture is re-entered unexpectedly, though less likely for session scope)
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(username='testuser', email='test@example.com')
            test_user.set_password('password')
            db.session.add(test_user)

        # Use db.session.get() for primary key lookups
        bulbasaur = db.session.get(Pokemon, 1)
        if not bulbasaur:
            bulbasaur = Pokemon(id=1, name='bulbasaur', type1='grass', type2='poison',
                                sprite_url='http://example.com/bulbasaur.png',
                                description='A strange seed was planted on its back at birth.')
            db.session.add(bulbasaur)

        db.session.commit()  # Commit the seeded data

    yield _app  # Provide the app instance to the tests

    # Teardown: This part runs after all tests in the session are complete
    with _app.app_context():
        db.session.remove()  # Good practice to remove session before dropping tables
        db.drop_all()        # Drop all tables

# Keep your other fixtures (client, runner, init_database, auth_client) as they were.
# The init_database fixture should look like this (ensure it has app_context too):


@pytest.fixture(scope='function')
def init_database(app):  # 'app' here is the session-scoped app fixture
    with app.app_context():  # Ensure operations are within app context
        db.drop_all()
        db.create_all()
        # Seed minimal data again if necessary for specific test modules/functions
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(username='testuser', email='test@example.com')
            test_user.set_password('password')
            db.session.add(test_user)

        bulbasaur = db.session.get(Pokemon, 1)
        if not bulbasaur:
            bulbasaur = Pokemon(id=1, name='bulbasaur', type1='grass', type2='poison',
                                sprite_url='http://example.com/bulbasaur.png', description='A strange seed was planted on its back at birth.')
            db.session.add(bulbasaur)
        db.session.commit()
    return db  # Not strictly necessary to return db, but fine.


@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """A test runner for the CLI."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def auth_client(client):  # Depends on 'client' which depends on 'app'
    """A test client that is logged in as 'testuser'."""
    # Ensure 'testuser' exists (app fixture should create it)
    # Use the app's context for url_for if needed, though client.post should handle it
    with client.application.app_context():
        login_url = '/auth/login'  # Hardcoding for simplicity or use url_for within context

    client.post(login_url, data=dict(
        identifier='testuser',
        password='password'
    ), follow_redirects=True)
    return client
