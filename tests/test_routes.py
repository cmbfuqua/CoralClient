import pytest
from datetime import datetime
from app import create_app
from app.extensions import db
from app.models import User, Role

@pytest.fixture(scope='function')
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        
        # Seed roles for testing only if they don't exist
        if not Role.query.filter_by(name='admin').first():
            admin_role = Role(name='admin')
            user_role = Role(name='user')
            db.session.add_all([admin_role, user_role])
            db.session.commit()
        
    yield app

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def admin_user(app):
    with app.app_context():
        admin_role = Role.query.filter_by(name='admin').first()
        user = User.query.filter_by(email='admin@test.com').first()
        if not user:
            user = User(
                username='testadmin',
                email='admin@test.com',
                password_hash='hashed',
                first_name='Admin',
                last_name='User',
                dob=datetime.utcnow().date(),
                phone_number='1234567890',
                role=admin_role,
                role_id=3
            )
            db.session.add(user)
            db.session.commit()
        return user

def test_home_page(client):
    """Test that the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    # Check for text that should be in base or home
    assert b"Corals4Cheap" in response.data

def test_login_page_load(client):
    """Test that the login page loads correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Welcome Back" in response.data

def test_core_catalog_routes(client):
    """Test standard catalog routes."""
    for path in ['/corals', '/fish', '/equipment']:
        response = client.get(path)
        assert response.status_code == 200

def test_admin_routes_redirect_unauthorized(client):
    """Test that admin routes redirect or error when not logged in."""
    admin_paths = [
        '/manage_users',
        '/manage_products',
        '/orders',
        '/admin/cleanup'
    ]
    for path in admin_paths:
        response = client.get(path)
        assert response.status_code in [302, 403]

def test_billing_blueprint_routing(app):
    """
    Test that billing routes are correctly registered
    and namespaced in the blueprint.
    """
    from flask import url_for
    with app.test_request_context():
        assert url_for('billing.view_all_bills') == '/view_all_bills'
        assert url_for('billing.customer_management') == '/customer_management'

def test_billing_pages_load_as_admin(client, admin_user):
    """Test that billing pages load correctly for an admin."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin_user.user_id)
    
    response = client.get('/view_all_bills')
    assert response.status_code == 200
