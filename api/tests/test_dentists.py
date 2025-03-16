import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from api.models import Clinic, ClinicMembership

@pytest.mark.django_db
class TestDentistEndpoints:
    """Test dentist endpoints."""
    
    @pytest.fixture
    def dentist_user(self):
        """Create and return a dentist user."""
        return User.objects.create_user(
            username='dentist',
            email='dentist@example.com',
            password='dentistpassword',
            first_name='Test',
            last_name='Dentist'
        )
    
    @pytest.fixture
    def dentist_membership(self, dentist_user, clinic):
        """Create and return a clinic membership for the dentist."""
        return ClinicMembership.objects.create(
            user=dentist_user,
            clinic=clinic,
            role='dentist',
            is_primary=True
        )
    
    @pytest.fixture
    def additional_dentist(self):
        """Create and return another dentist user."""
        return User.objects.create_user(
            username='dentist2',
            email='dentist2@example.com',
            password='dentistpassword',
            first_name='Second',
            last_name='Dentist'
        )
    
    @pytest.fixture
    def additional_dentist_membership(self, additional_dentist, clinic):
        """Create and return a clinic membership for the additional dentist."""
        return ClinicMembership.objects.create(
            user=additional_dentist,
            clinic=clinic,
            role='dentist',
            is_primary=True
        )
    
    def test_list_dentists(self, authenticated_client, user, clinic, clinic_membership, 
                          dentist_user, dentist_membership, additional_dentist, additional_dentist_membership):
        """Test listing dentists for a clinic."""
        url = reverse('clinic-dentist-list', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 2  # Should include both dentists
        
        # Verify dentist data is correct
        dentist_ids = [d['id'] for d in response.data['results']]
        assert dentist_user.id in dentist_ids
        assert additional_dentist.id in dentist_ids
        
        # Check that the response includes the expected fields
        for dentist_data in response.data['results']:
            assert 'id' in dentist_data
            assert 'username' in dentist_data
            assert 'first_name' in dentist_data
            assert 'last_name' in dentist_data
            assert 'email' in dentist_data
    
    def test_dentist_access_control(self, authenticated_client, user, clinic, clinic_membership,
                                   dentist_user, dentist_membership, additional_dentist, additional_dentist_membership):
        """Test that users can only access dentists from clinics they are members of."""
        # Create another clinic
        other_clinic = Clinic.objects.create(
            name='Other Clinic',
            address='456 Other St',
            phone='9876543210',
            email='other@example.com'
        )
        
        # Add the additional dentist to the other clinic
        ClinicMembership.objects.create(
            user=additional_dentist,
            clinic=other_clinic,
            role='dentist',
            is_primary=False
        )
        
        # Try to access dentists from the other clinic
        url = reverse('clinic-dentist-list', args=[other_clinic.id])
        response = authenticated_client.get(url)
        
        # Should get 403 Forbidden since the authenticated user is not a member of other_clinic
        assert response.status_code == status.HTTP_403_FORBIDDEN 