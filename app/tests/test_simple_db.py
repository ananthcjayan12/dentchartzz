import pytest
from django.contrib.auth.models import User
import uuid


@pytest.mark.django_db
def test_create_user():
    """Test that a user can be created."""
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = User.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='testpassword'
    )
    assert User.objects.filter(username=username).exists()
    assert user.email == f'{username}@example.com' 