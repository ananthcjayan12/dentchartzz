import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import Clinic, ClinicMembership

@pytest.fixture
def api_client():
    """Return an API client for testing."""
    return APIClient()

@pytest.fixture
def user():
    """Create and return a regular user."""
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpassword'
    )

@pytest.fixture
def admin_user():
    """Create and return an admin user."""
    return User.objects.create_user(
        username='adminuser',
        email='adminuser@example.com',
        password='adminpassword',
        is_staff=True,
        is_superuser=True
    )

@pytest.fixture
def clinic():
    """Create and return a clinic."""
    return Clinic.objects.create(
        name='Test Clinic',
        address='123 Test Street',
        phone='1234567890',
        email='clinic@example.com',
        subscription_plan='basic',
        subscription_status='active'
    )

@pytest.fixture
def clinic_membership(user, clinic):
    """Create and return a clinic membership for the user."""
    return ClinicMembership.objects.create(
        user=user,
        clinic=clinic,
        role='admin',
        is_primary=True
    )

@pytest.fixture
def admin_membership(admin_user, clinic):
    """Create and return a clinic membership for the admin user."""
    return ClinicMembership.objects.create(
        user=admin_user,
        clinic=clinic,
        role='admin',
        is_primary=True
    )

@pytest.fixture
def authenticated_client(api_client, user):
    """Return an authenticated API client."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client

@pytest.fixture
def admin_client(api_client, admin_user):
    """Return an authenticated API client for an admin user."""
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client 