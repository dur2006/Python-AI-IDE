"""
Pytest Configuration and Fixtures
Provides shared fixtures and configuration for all tests
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

from backend.database import DatabaseManager, init_database
from backend.database.models import User, Project, Theme, Extension, Layout, UserSettings
from backend.services.security_service import SecurityService
from backend.services.terminal_service_secure import SecureTerminalService
from backend.services.appdata_manager import AppDataManager


@pytest.fixture(scope='session')
def temp_dir():
    """Create a temporary directory for test data"""
    temp_path = tempfile.mkdtemp(prefix='autopilot_test_')
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope='function')
def test_db(temp_dir):
    """Create a test database for each test function"""
    db_path = temp_dir / 'test.db'
    db_url = f'sqlite:///{db_path}'
    
    # Create database manager
    db_manager = DatabaseManager(db_url, echo=False)
    db_manager.init_db(drop_all=True)
    
    yield db_manager
    
    # Cleanup
    db_manager.close()
    if db_path.exists():
        db_path.unlink()


@pytest.fixture(scope='function')
def db_session(test_db):
    """Provide a database session for tests"""
    with test_db.get_session() as session:
        yield session


@pytest.fixture(scope='function')
def test_user(db_session):
    """Create a test user"""
    from backend.services.security_service import get_security_service
    
    security = get_security_service()
    
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=security.hash_password('testpassword123'),
        full_name='Test User',
        is_active=True,
        is_admin=False
    )
    
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    return user


@pytest.fixture(scope='function')
def test_admin(db_session):
    """Create a test admin user"""
    from backend.services.security_service import get_security_service
    
    security = get_security_service()
    
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=security.hash_password('adminpassword123'),
        full_name='Admin User',
        is_active=True,
        is_admin=True
    )
    
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    
    return admin


@pytest.fixture(scope='function')
def test_project(db_session, test_user):
    """Create a test project"""
    project = Project(
        owner_id=test_user.id,
        name='Test Project',
        description='A test project',
        path='./projects/test-project',
        project_type='Python',
        is_active=True
    )
    
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    
    return project


@pytest.fixture(scope='function')
def test_theme(db_session):
    """Create a test theme"""
    theme = Theme(
        name='Test Theme',
        description='A test theme',
        is_default=False,
        is_active=False,
        colors={
            'primary': '#667eea',
            'background': '#1e1e1e',
            'text': '#d4d4d4'
        }
    )
    
    db_session.add(theme)
    db_session.commit()
    db_session.refresh(theme)
    
    return theme


@pytest.fixture(scope='function')
def test_extension(db_session):
    """Create a test extension"""
    extension = Extension(
        name='Test Extension',
        description='A test extension',
        version='1.0.0',
        author='Test Author',
        icon='test',
        is_installed=False,
        is_enabled=False
    )
    
    db_session.add(extension)
    db_session.commit()
    db_session.refresh(extension)
    
    return extension


@pytest.fixture(scope='function')
def test_layout(db_session):
    """Create a test layout"""
    layout = Layout(
        name='Test Layout',
        description='A test layout',
        is_default=False,
        is_active=False,
        config={
            'sidebar': {'visible': True, 'width': 250},
            'editor': {'visible': True},
            'terminal': {'visible': True, 'height': 250},
            'aiPanel': {'visible': True, 'width': 380}
        }
    )
    
    db_session.add(layout)
    db_session.commit()
    db_session.refresh(layout)
    
    return layout


@pytest.fixture(scope='function')
def security_service():
    """Provide a security service instance"""
    return SecurityService()


@pytest.fixture(scope='function')
def terminal_service():
    """Provide a terminal service instance"""
    return SecureTerminalService()


@pytest.fixture(scope='function')
def appdata_manager(temp_dir):
    """Provide an AppData manager instance with temp directory"""
    manager = AppDataManager()
    manager.data_dir = temp_dir
    manager.projects_file = temp_dir / 'projects.json'
    manager.themes_file = temp_dir / 'themes.json'
    manager.extensions_file = temp_dir / 'extensions.json'
    manager.layouts_file = temp_dir / 'layouts.json'
    manager.settings_file = temp_dir / 'settings.json'
    manager.initialize()
    
    return manager


@pytest.fixture(scope='function')
def mock_flask_app(test_db):
    """Create a mock Flask app for testing"""
    from flask import Flask
    
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['PROJECTS_DIR'] = Path(tempfile.mkdtemp())
    app.config['TERMINAL_TIMEOUT'] = 5
    app.config['TERMINAL_MAX_OUTPUT'] = 1000
    
    with app.app_context():
        yield app
    
    # Cleanup
    if app.config['PROJECTS_DIR'].exists():
        shutil.rmtree(app.config['PROJECTS_DIR'], ignore_errors=True)


@pytest.fixture(scope='function')
def client(mock_flask_app):
    """Provide a Flask test client"""
    return mock_flask_app.test_client()


@pytest.fixture(scope='function')
def auth_headers(test_user, security_service):
    """Provide authentication headers for API requests"""
    token = security_service.generate_session_token(str(test_user.id), '127.0.0.1')
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture(scope='function')
def admin_headers(test_admin, security_service):
    """Provide admin authentication headers for API requests"""
    token = security_service.generate_session_token(str(test_admin.id), '127.0.0.1')
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


# Utility functions for tests

def create_test_file(directory: Path, filename: str, content: str = '') -> Path:
    """Create a test file with content"""
    file_path = directory / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    return file_path


def assert_dict_contains(actual: dict, expected: dict):
    """Assert that actual dict contains all keys/values from expected dict"""
    for key, value in expected.items():
        assert key in actual, f"Key '{key}' not found in actual dict"
        assert actual[key] == value, f"Value mismatch for key '{key}': expected {value}, got {actual[key]}"


def assert_response_success(response, status_code: int = 200):
    """Assert that API response is successful"""
    assert response.status_code == status_code, f"Expected status {status_code}, got {response.status_code}"
    if response.content_type == 'application/json':
        data = response.get_json()
        assert 'error' not in data or not data['error'], f"Response contains error: {data.get('error')}"


def assert_response_error(response, status_code: int = 400):
    """Assert that API response is an error"""
    assert response.status_code == status_code, f"Expected status {status_code}, got {response.status_code}"
    if response.content_type == 'application/json':
        data = response.get_json()
        assert 'error' in data, "Response should contain error message"


# Pytest configuration

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security-related"
    )
    config.addinivalue_line(
        "markers", "database: mark test as database-related"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add markers based on test location
        if "test_security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        if "test_database" in str(item.fspath):
            item.add_marker(pytest.mark.database)
        if "test_integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
