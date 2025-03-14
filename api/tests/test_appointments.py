import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
from api.models import Appointment, Patient, Clinic, ClinicMembership

@pytest.mark.django_db
class TestAppointmentEndpoints:
    """Test appointment endpoints."""
    
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
    def dentist(self):
        """Create and return a dentist user."""
        return User.objects.create_user(
            username='dentist',
            email='dentist@example.com',
            password='dentistpassword',
            first_name='Test',
            last_name='Dentist'
        )
    
    @pytest.fixture
    def dentist_membership(self, dentist, clinic):
        """Create and return a clinic membership for the dentist."""
        return ClinicMembership.objects.create(
            user=dentist,
            clinic=clinic,
            role='dentist',
            is_primary=True
        )
    
    @pytest.fixture
    def appointment(self, clinic, patient, dentist):
        """Create and return a test appointment."""
        tomorrow = date.today() + timedelta(days=1)
        return Appointment.objects.create(
            clinic=clinic,
            patient=patient,
            dentist=dentist,
            date=tomorrow,
            start_time='10:00:00',
            end_time='10:30:00',
            status='scheduled',
            notes='Regular checkup'
        )
    
    def test_list_appointments(self, authenticated_client, user, clinic, clinic_membership, patient, dentist, dentist_membership, appointment):
        """Test listing appointments."""
        # Create another appointment
        next_week = date.today() + timedelta(days=7)
        Appointment.objects.create(
            clinic=clinic,
            patient=patient,
            dentist=dentist,
            date=next_week,
            start_time='14:00:00',
            end_time='14:30:00',
            status='scheduled',
            notes='Follow-up'
        )
        
        url = reverse('clinic-appointment-list', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Test filtering by date range
        url = f"{reverse('clinic-appointment-list', args=[clinic.id])}?start_date={next_week}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        # The basic AppointmentSerializer doesn't include notes, so we can't check for it
        # Instead, check for the date
        assert response.data['results'][0]['date'] == next_week.strftime('%Y-%m-%d')
        
        # Test filtering by status
        url = f"{reverse('clinic-appointment-list', args=[clinic.id])}?status=scheduled"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Test filtering by patient
        url = f"{reverse('clinic-appointment-list', args=[clinic.id])}?patient_id={patient.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Test filtering by dentist
        url = f"{reverse('clinic-appointment-list', args=[clinic.id])}?dentist_id={dentist.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_create_appointment(self, authenticated_client, user, clinic, clinic_membership, patient, dentist, dentist_membership):
        """Test creating an appointment."""
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        url = reverse('clinic-appointment-list', args=[clinic.id])
        data = {
            'patient_id': patient.id,
            'dentist_id': dentist.id,
            'date': tomorrow,
            'start_time': '11:00:00',
            'end_time': '11:30:00',
            'notes': 'New appointment'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['patient']['id'] == patient.id
        assert response.data['dentist']['id'] == dentist.id
        assert response.data['date'] == tomorrow
        assert response.data['start_time'] == '11:00:00'
        assert response.data['end_time'] == '11:30:00'
        assert response.data['notes'] == 'New appointment'
        assert response.data['status'] == 'scheduled'
        
        # Verify the appointment was created in the database
        appointment = Appointment.objects.get(notes='New appointment')
        assert appointment.clinic == clinic
        assert appointment.patient == patient
        assert appointment.dentist == dentist
    
    def test_get_appointment_detail(self, authenticated_client, user, clinic, clinic_membership, appointment):
        """Test getting appointment details."""
        url = reverse('clinic-appointment-detail', args=[clinic.id, appointment.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == appointment.id
        assert response.data['patient']['name'] == 'Test Patient'
        assert response.data['dentist']['username'] == 'dentist'
        assert response.data['status'] == 'scheduled'
        assert response.data['notes'] == 'Regular checkup'
    
    def test_update_appointment(self, authenticated_client, user, clinic, clinic_membership, appointment):
        """Test updating an appointment."""
        url = reverse('clinic-appointment-detail', args=[clinic.id, appointment.id])
        data = {
            'start_time': '11:00:00',
            'end_time': '11:45:00',
            'notes': 'Updated notes'
        }
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['start_time'] == '11:00:00'
        assert response.data['end_time'] == '11:45:00'
        assert response.data['notes'] == 'Updated notes'
        
        # Verify the appointment was updated in the database
        appointment.refresh_from_db()
        assert str(appointment.start_time) == '11:00:00'
        assert str(appointment.end_time) == '11:45:00'
        assert appointment.notes == 'Updated notes'
    
    def test_cancel_appointment(self, authenticated_client, user, clinic, clinic_membership, appointment):
        """Test canceling an appointment."""
        url = reverse('clinic-appointment-cancel', args=[clinic.id, appointment.id])
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'cancelled'
        
        # Verify the appointment was cancelled in the database
        appointment.refresh_from_db()
        assert appointment.status == 'cancelled'
        
        # Test canceling an already cancelled appointment
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_appointment_status(self, authenticated_client, user, clinic, clinic_membership, appointment):
        """Test updating appointment status."""
        url = reverse('clinic-appointment-update-status', args=[clinic.id, appointment.id])
        
        # Test updating to completed
        data = {'status': 'completed'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'completed'
        
        # Verify the status was updated in the database
        appointment.refresh_from_db()
        assert appointment.status == 'completed'
        
        # Test updating to no_show
        data = {'status': 'no_show'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'no_show'
        
        # Test with invalid status
        data = {'status': 'invalid_status'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test without status
        data = {}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_time_slots(self, authenticated_client, user, clinic, clinic_membership, dentist, dentist_membership, appointment):
        """Test getting available time slots."""
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        url = f"{reverse('clinic-appointment-time-slots', args=[clinic.id])}?date={tomorrow}&dentist_id={dentist.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        
        # Check that the time slot of the existing appointment is not available
        for slot in response.data:
            assert slot['start_time'] != '10:00:00'
        
        # Test without required parameters
        url = f"{reverse('clinic-appointment-time-slots', args=[clinic.id])}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        url = f"{reverse('clinic-appointment-time-slots', args=[clinic.id])}?date={tomorrow}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        url = f"{reverse('clinic-appointment-time-slots', args=[clinic.id])}?dentist_id={dentist.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_appointment_from_different_clinic(self, authenticated_client, user, clinic, clinic_membership, patient, dentist, dentist_membership):
        """Test that a user cannot access appointments from a different clinic."""
        # Create another clinic
        other_clinic = Clinic.objects.create(
            name='Other Clinic',
            address='Other Address',
            phone='9999999999',
            email='other@example.com'
        )
        
        # Create a patient in the other clinic
        other_patient = Patient.objects.create(
            clinic=other_clinic,
            name='Other Patient',
            age=50,
            gender='M',
            phone='8888888888'
        )
        
        # Create an appointment in the other clinic
        tomorrow = date.today() + timedelta(days=1)
        other_appointment = Appointment.objects.create(
            clinic=other_clinic,
            patient=other_patient,
            dentist=dentist,
            date=tomorrow,
            start_time='10:00:00',
            end_time='10:30:00',
            status='scheduled',
            notes='Other clinic appointment'
        )
        
        # Try to access the appointment from the other clinic
        url = reverse('clinic-appointment-detail', args=[clinic.id, other_appointment.id])
        response = authenticated_client.get(url)
        
        # Should return 404 because the appointment doesn't exist in this clinic
        assert response.status_code == status.HTTP_404_NOT_FOUND 