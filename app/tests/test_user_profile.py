import pytest
from django.contrib.auth.models import User
from app.models import UserProfile
import uuid


@pytest.mark.django_db
def test_create_user_profile():
    """Test that a user profile can be created."""
    # Delete all existing UserProfile objects
    UserProfile.objects.all().delete()
    
    # Delete all existing User objects
    User.objects.all().delete()
    
    # Create a new user
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='testpassword'
    )
    
    # Check if a profile was automatically created by the signal
    profile = UserProfile.objects.get(user=user)
    
    # Update the profile instead of creating a new one
    profile.role = 'dentist'
    profile.phone = '1234567890'
    profile.address = '123 Test Street'
    profile.save()
    
    # Verify the profile was updated
    updated_profile = UserProfile.objects.get(user=user)
    assert updated_profile.role == 'dentist'
    assert updated_profile.phone == '1234567890'
    assert updated_profile.address == '123 Test Street' 