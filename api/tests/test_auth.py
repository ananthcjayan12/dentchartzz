import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.mark.django_db
class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_login(self, api_client, user):
        """Test user login."""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
    
    def test_login_invalid_credentials(self, api_client, user):
        """Test login with invalid credentials."""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_refresh_token(self, api_client, user):
        """Test token refresh."""
        refresh = RefreshToken.for_user(user)
        url = reverse('token_refresh')
        data = {
            'refresh': str(refresh)
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
    
    def test_register(self, api_client):
        """Test user registration."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'password2': 'newpassword123',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'refresh' in response.data
        assert 'access' in response.data
        assert 'user' in response.data
        assert User.objects.filter(username='newuser').exists()
    
    def test_register_passwords_dont_match(self, api_client):
        """Test registration with mismatched passwords."""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'password2': 'differentpassword',
            'email': 'newuser@example.com'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(username='newuser').exists()
    
    def test_logout(self, authenticated_client, user):
        """Test user logout."""
        refresh = RefreshToken.for_user(user)
        url = reverse('logout')
        data = {
            'refresh': str(refresh)
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_205_RESET_CONTENT
    
    def test_user_info(self, authenticated_client, user, clinic, clinic_membership):
        """Test getting user info."""
        url = reverse('user_info')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data
        assert 'clinics' in response.data
        assert 'current_clinic' in response.data
        assert response.data['user']['username'] == user.username
        assert len(response.data['clinics']) == 1
        assert response.data['clinics'][0]['name'] == clinic.name
    
    def test_select_clinic(self, authenticated_client, user, clinic, clinic_membership):
        """Test selecting a clinic."""
        url = reverse('select_clinic')
        data = {
            'clinic_id': clinic.id
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'clinic' in response.data
        assert response.data['clinic']['id'] == clinic.id
    
    def test_change_password(self, authenticated_client, user):
        """Test changing password."""
        url = reverse('change_password')
        data = {
            'old_password': 'testpassword',
            'new_password': 'newtestpassword123'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify the password was changed
        user.refresh_from_db()
        assert user.check_password('newtestpassword123') 