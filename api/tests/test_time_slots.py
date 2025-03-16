import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from datetime import date, timedelta, time
from api.models import Clinic, ClinicMembership, Patient, Appointment

@pytest.mark.django_db
class TestTimeSlotEndpoints:
    """Test time slot endpoints."""
    
    @pytest.fixture
    def patient(self, clinic):
        """Create and return a test patient."""
        return Patient.objects.create(
            clinic=clinic,
            name='Test Patient',
            age=30,
            gender='M',
            phone='1234567890'
        )
    
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
    def appointment(self, clinic, patient, dentist_user):
        """Create and return a test appointment."""
        tomorrow = date.today() + timedelta(days=1)
        return Appointment.objects.create(
            clinic=clinic,
            patient=patient,
            dentist=dentist_user,
            date=tomorrow,
            start_time=time(10, 0),  # 10:00 AM
            end_time=time(10, 30),   # 10:30 AM
            status='scheduled',
            notes='Regular checkup'
        )
    
    def test_get_time_slots(self, authenticated_client, user, clinic, clinic_membership, 
                           dentist_user, dentist_membership, appointment):
        """Test getting available time slots for a dentist on a specific date."""
        tomorrow = date.today() + timedelta(days=1)
        url = reverse('time_slots', args=[clinic.id])
        
        # Add query parameters
        query_params = {
            'dentist': dentist_user.id,
            'date': tomorrow.strftime('%Y-%m-%d')
        }
        
        response = authenticated_client.get(url, query_params)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Parse the JSON response
        data = response.json()
        
        assert 'time_slots' in data
        
        # Check that we have time slots from 9 AM to 5 PM (16 slots for 30-minute intervals)
        assert len(data['time_slots']) == 16
        
        # Check that the 10:00 AM slot is marked as unavailable (due to existing appointment)
        for slot in data['time_slots']:
            if slot['time'] == '10:00':
                assert slot['available'] is False
            else:
                assert slot['available'] is True
    
    def test_get_time_slots_with_selected_time(self, authenticated_client, user, clinic, clinic_membership, 
                                              dentist_user, dentist_membership):
        """Test getting time slots with a selected time."""
        tomorrow = date.today() + timedelta(days=1)
        url = reverse('time_slots', args=[clinic.id])
        
        # Add query parameters with selected time
        query_params = {
            'dentist': dentist_user.id,
            'date': tomorrow.strftime('%Y-%m-%d'),
            'selected_time': '11:00'
        }
        
        response = authenticated_client.get(url, query_params)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check that the 11:00 AM slot is marked as selected
        for slot in response.data['time_slots']:
            if slot['time'] == '11:00':
                assert slot['selected'] is True
            else:
                assert slot['selected'] is False
    
    def test_get_time_slots_missing_parameters(self, authenticated_client, user, clinic, clinic_membership):
        """Test getting time slots with missing parameters."""
        url = reverse('time_slots', args=[clinic.id])
        
        # Missing dentist parameter
        response = authenticated_client.get(url, {'date': '2023-01-01'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Missing date parameter
        response = authenticated_client.get(url, {'dentist': 1})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_time_slots_invalid_date(self, authenticated_client, user, clinic, clinic_membership, dentist_user):
        """Test getting time slots with invalid date format."""
        url = reverse('time_slots', args=[clinic.id])
        
        # Invalid date format
        response = authenticated_client.get(url, {'dentist': dentist_user.id, 'date': 'invalid-date'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST