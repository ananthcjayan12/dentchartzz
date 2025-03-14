import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from datetime import date, timedelta
from api.models import Treatment, Tooth, ToothCondition, Patient, Clinic, ClinicMembership, Appointment

@pytest.mark.django_db
class TestTreatmentEndpoints:
    """Test treatment endpoints."""
    
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
    
    @pytest.fixture
    def tooth(self):
        """Create and return a test tooth."""
        return Tooth.objects.create(
            number=11,
            name='Upper Right Central Incisor',
            quadrant=1,
            position=1
        )
    
    @pytest.fixture
    def tooth_condition(self, clinic):
        """Create and return a test tooth condition."""
        return ToothCondition.objects.create(
            clinic=clinic,
            name='Cavity',
            description='Dental caries'
        )
    
    @pytest.fixture
    def treatment(self, clinic, patient, tooth, tooth_condition, appointment):
        """Create and return a test treatment."""
        return Treatment.objects.create(
            clinic=clinic,
            patient=patient,
            tooth=tooth,
            condition=tooth_condition,
            appointment=appointment,
            description='Filling needed',
            status='planned',
            cost=100.00
        )
    
    def test_list_treatments(self, authenticated_client, user, clinic, clinic_membership, patient, tooth, tooth_condition, appointment, treatment):
        """Test listing treatments."""
        # Create another treatment
        Treatment.objects.create(
            clinic=clinic,
            patient=patient,
            tooth=tooth,
            condition=tooth_condition,
            appointment=appointment,
            description='Root canal needed',
            status='planned',
            cost=200.00
        )
        
        url = reverse('clinic-treatment-list', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Test filtering by patient
        url = f"{reverse('clinic-treatment-list', args=[clinic.id])}?patient_id={patient.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Test filtering by tooth
        url = f"{reverse('clinic-treatment-list', args=[clinic.id])}?tooth_id={tooth.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Test filtering by status
        url = f"{reverse('clinic-treatment-list', args=[clinic.id])}?status=planned"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Test filtering by appointment
        url = f"{reverse('clinic-treatment-list', args=[clinic.id])}?appointment_id={appointment.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_create_treatment(self, authenticated_client, user, clinic, clinic_membership, patient, tooth, tooth_condition, appointment):
        """Test creating a treatment."""
        url = reverse('clinic-treatment-list', args=[clinic.id])
        data = {
            'patient_id': patient.id,
            'tooth_id': tooth.id,
            'condition_id': tooth_condition.id,
            'appointment_id': appointment.id,
            'description': 'New treatment',
            'status': 'planned',
            'cost': 150.00
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['patient']['id'] == patient.id
        assert response.data['tooth']['id'] == tooth.id
        assert response.data['condition']['id'] == tooth_condition.id
        assert response.data['appointment']['id'] == appointment.id
        assert response.data['description'] == 'New treatment'
        assert response.data['status'] == 'planned'
        assert float(response.data['cost']) == 150.00
        
        # Verify the treatment was created in the database
        treatment = Treatment.objects.get(description='New treatment')
        assert treatment.clinic == clinic
        assert treatment.patient == patient
        assert treatment.tooth == tooth
        assert treatment.condition == tooth_condition
        assert treatment.appointment == appointment
    
    def test_get_treatment_detail(self, authenticated_client, user, clinic, clinic_membership, treatment):
        """Test getting treatment details."""
        url = reverse('clinic-treatment-detail', args=[clinic.id, treatment.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == treatment.id
        assert response.data['patient']['name'] == 'Test Patient'
        assert response.data['tooth']['number'] == 11
        assert response.data['condition']['name'] == 'Cavity'
        assert response.data['description'] == 'Filling needed'
        assert response.data['status'] == 'planned'
        assert float(response.data['cost']) == 100.00
    
    def test_update_treatment(self, authenticated_client, user, clinic, clinic_membership, treatment):
        """Test updating a treatment."""
        url = reverse('clinic-treatment-detail', args=[clinic.id, treatment.id])
        data = {
            'description': 'Updated description',
            'cost': 120.00
        }
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['description'] == 'Updated description'
        assert float(response.data['cost']) == 120.00
        
        # Verify the treatment was updated in the database
        treatment.refresh_from_db()
        assert treatment.description == 'Updated description'
        assert treatment.cost == 120.00
    
    def test_update_treatment_status(self, authenticated_client, user, clinic, clinic_membership, treatment):
        """Test updating treatment status."""
        url = reverse('clinic-treatment-update-status', args=[clinic.id, treatment.id])
        
        # Test updating to in_progress
        data = {'status': 'in_progress', 'notes': 'Started treatment'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'in_progress'
        
        # Verify the status was updated in the database
        treatment.refresh_from_db()
        assert treatment.status == 'in_progress'
        
        # Verify a treatment history entry was created
        history = treatment.history.first()
        assert history is not None
        assert history.previous_status == 'planned'
        assert history.new_status == 'in_progress'
        assert history.notes == 'Started treatment'
        
        # Test updating to completed
        data = {'status': 'completed', 'notes': 'Finished treatment'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'completed'
        
        # Verify the status was updated in the database
        treatment.refresh_from_db()
        assert treatment.status == 'completed'
        
        # Test with invalid status
        data = {'status': 'invalid_status'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test without status
        data = {'notes': 'No status provided'}
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_treatments_by_tooth(self, authenticated_client, user, clinic, clinic_membership, patient, tooth, tooth_condition, treatment):
        """Test getting treatments for a specific tooth."""
        url = f"{reverse('clinic-treatment-by-tooth', args=[clinic.id])}?patient_id={patient.id}&tooth_id={tooth.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['tooth_number'] == 11
        
        # Test without required parameters
        url = f"{reverse('clinic-treatment-by-tooth', args=[clinic.id])}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        url = f"{reverse('clinic-treatment-by-tooth', args=[clinic.id])}?patient_id={patient.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        url = f"{reverse('clinic-treatment-by-tooth', args=[clinic.id])}?tooth_id={tooth.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_list_teeth(self, authenticated_client, user, clinic, clinic_membership, tooth):
        """Test listing teeth."""
        # Create another tooth
        Tooth.objects.create(
            number=21,
            name='Upper Left Central Incisor',
            quadrant=2,
            position=1
        )
        
        url = reverse('clinic-tooth-list', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Verify the teeth are returned in order by number
        assert response.data['results'][0]['number'] == 11
        assert response.data['results'][1]['number'] == 21
    
    def test_get_tooth_detail(self, authenticated_client, user, clinic, clinic_membership, tooth):
        """Test getting tooth details."""
        url = reverse('clinic-tooth-detail', args=[clinic.id, tooth.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == tooth.id
        assert response.data['number'] == 11
        assert response.data['name'] == 'Upper Right Central Incisor'
        assert response.data['quadrant'] == 1
        assert response.data['quadrant_display'] == 'Upper Right'
        assert response.data['position'] == 1
    
    def test_get_tooth_treatments(self, authenticated_client, user, clinic, clinic_membership, tooth, treatment):
        """Test getting treatments for a tooth."""
        url = reverse('clinic-tooth-treatments', args=[clinic.id, tooth.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['tooth_number'] == 11
        assert response.data[0]['description'] == 'Filling needed'
    
    def test_treatment_from_different_clinic(self, authenticated_client, user, clinic, clinic_membership, patient, tooth, tooth_condition):
        """Test that a user cannot access treatments from a different clinic."""
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
        
        # Create a tooth condition in the other clinic
        other_condition = ToothCondition.objects.create(
            clinic=other_clinic,
            name='Other Cavity',
            description='Other dental caries'
        )
        
        # Create a treatment in the other clinic
        other_treatment = Treatment.objects.create(
            clinic=other_clinic,
            patient=other_patient,
            tooth=tooth,
            condition=other_condition,
            description='Other filling needed',
            status='planned',
            cost=100.00
        )
        
        # Try to access the treatment from the other clinic
        url = reverse('clinic-treatment-detail', args=[clinic.id, other_treatment.id])
        response = authenticated_client.get(url)
        
        # Should return 404 because the treatment doesn't exist in this clinic
        assert response.status_code == status.HTTP_404_NOT_FOUND 