import pytest
from app import app as flask_app
from DB import db
from models import User, Role

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with flask_app.app_context():
        db.create_all()
        
        # Seed roles for testing
        admin_role = Role(name='admin')
        user_role = Role(name='user')
        db.session.add_all([admin_role, user_role])
        db.session.commit()
        
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def admin_user(app):
    with app.app_context():
        admin_role = Role.query.filter_by(name='admin').first()
        user = User(
            username='testadmin',
            email='admin@test.com',
            password_hash='hashed',
            first_name='Admin',
            last_name='User',
            role=admin_role,
            is_admin=True
        )
        db.session.add(user)
        db.session.commit()
        return user

def test_home_page(client):
    """Test that the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"A Living Masterpiece" in response.data

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
        # Should redirect to login or home
        assert response.status_code in [302, 403]

def test_billing_blueprint_routing(client):
    """
    Test that billing routes (which caused BuildErrors) are correctly registered
    and namespaced in the blueprint.
    """
    from flask import url_for
    with flask_app.test_request_context():
        # These are the ones that were failing with BuildErrors
        assert url_for('billing.view_all_bills') == '/view_all_bills'
        assert url_for('billing.customer_management') == '/customer_management'
        assert url_for('billing.create_maintenance_visit') == '/create_maintenance_visit'
        assert url_for('billing.add_maintenance_customer') == '/add_maintenance_customer'

def test_billing_pages_load_as_admin(client, admin_user):
    """Test that billing pages load correctly for an admin."""
    # Login the admin user
    with client.session_transaction() as sess:
        sess['_user_id'] = admin_user.user_id
    
    # Test billing dashboard
    response = client.get('/view_all_bills')
    assert response.status_code == 200
    assert b"Billing Dashboard" in response.data

def test_user_management_as_admin(client, admin_user):
    """Test admin-only user management page."""
    with client.session_transaction() as sess:
        sess['_user_id'] = admin_user.user_id
        
    response = client.get('/manage_users')
    assert response.status_code == 200
    assert b"User Management" in response.data
