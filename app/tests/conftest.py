import pytest
from django.contrib.auth.models import User
from app.models import UserProfile, Patient, Tooth, ToothCondition
import uuid
from django.db import connections


@pytest.fixture(autouse=True)
def db_reset(django_db_setup, django_db_blocker):
    """Reset the database before each test."""
    with django_db_blocker.unblock():
        # Clear all tables
        for connection in connections.all():
            with connection.cursor() as cursor:
                tables = connection.introspection.table_names()
                for table in tables:
                    if table.startswith('app_') or table.startswith('auth_'):
                        cursor.execute(f"DELETE FROM {table}")


@pytest.fixture
def create_user():
    """Fixture to create a user with a unique username."""
    def _create_user(role='staff', phone=None, address=None):
        username = f"testuser_{uuid.uuid4().hex[:8]}"
        user = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='testpassword'
        )
        
        # Get the profile that was automatically created by the signal
        profile = UserProfile.objects.get(user=user)
        
        # Update the profile with the provided role and other attributes
        profile.role = role
        if phone:
            profile.phone = phone
        if address:
            profile.address = address
        profile.save()
        
        return user, profile
    return _create_user


@pytest.fixture
def staff_user(create_user):
    """Fixture to create a staff user."""
    user, profile = create_user(role='staff')
    return user


@pytest.fixture
def dentist_user(create_user):
    """Fixture to create a dentist user."""
    user, profile = create_user(role='dentist')
    return user


@pytest.fixture
def admin_user(create_user):
    """Fixture to create an admin user."""
    user, profile = create_user(role='admin')
    return user


@pytest.fixture
def patient():
    """Fixture to create a test patient."""
    return Patient.objects.create(
        name='Test Patient',
        age=30,
        gender='M',
        phone='1234567890',
        address='123 Test Street',
        chief_complaint='Toothache'
    )


@pytest.fixture
def tooth():
    """Fixture to create a test tooth."""
    return Tooth.objects.create(
        number=11,
        name='Upper Right Central Incisor',
        quadrant=1,
        position=1
    )


@pytest.fixture
def tooth_condition():
    """Fixture to create a test tooth condition."""
    return ToothCondition.objects.create(
        name='Cavity',
        description='Dental decay requiring filling'
    ) 