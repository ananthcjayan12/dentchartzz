import pytest
from django.urls import reverse
from rest_framework import status
from api.models import Patient

@pytest.mark.django_db
class TestPatientEndpoints:
    """Test patient endpoints."""
    
    def test_list_patients(self, authenticated_client, user, clinic, clinic_membership):
        """Test listing patients."""
        # Create some test patients
        Patient.objects.create(
            clinic=clinic,
            name='Test Patient 1',
            age=30,
            gender='M',
            phone='1234567890'
        )
        Patient.objects.create(
            clinic=clinic,
            name='Test Patient 2',
            age=25,
            gender='F',
            phone='0987654321'
        )
        
        url = reverse('clinic-patient-list', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        assert response.data['results'][0]['name'] in ['Test Patient 1', 'Test Patient 2']
        assert response.data['results'][1]['name'] in ['Test Patient 1', 'Test Patient 2']
    
    def test_create_patient(self, authenticated_client, user, clinic, clinic_membership):
        """Test creating a patient."""
        url = reverse('clinic-patient-list', args=[clinic.id])
        data = {
            'name': 'New Patient',
            'age': 40,
            'gender': 'M',
            'phone': '5555555555',
            'email': 'newpatient@example.com',
            'address': '789 Patient St',
            'chief_complaint': 'Toothache',
            'medical_history': 'None',
            'drug_allergies': 'None',
            'previous_dental_work': 'Fillings'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Patient'
        assert response.data['age'] == 40
        assert response.data['gender'] == 'M'
        
        # Verify the patient was created in the database
        patient = Patient.objects.get(name='New Patient')
        assert patient.clinic == clinic
        assert patient.age == 40
        assert patient.chief_complaint == 'Toothache'
    
    def test_get_patient_detail(self, authenticated_client, user, clinic, clinic_membership):
        """Test getting patient details."""
        patient = Patient.objects.create(
            clinic=clinic,
            name='Detail Patient',
            age=35,
            gender='F',
            phone='1112223333',
            email='detail@example.com',
            address='123 Detail St',
            chief_complaint='Sensitivity',
            medical_history='Hypertension',
            drug_allergies='Penicillin',
            previous_dental_work='Root canal'
        )
        
        url = reverse('clinic-patient-detail', args=[clinic.id, patient.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Detail Patient'
        assert response.data['age'] == 35
        assert response.data['gender'] == 'F'
        assert response.data['chief_complaint'] == 'Sensitivity'
        assert response.data['medical_history'] == 'Hypertension'
        assert response.data['drug_allergies'] == 'Penicillin'
    
    def test_update_patient(self, authenticated_client, user, clinic, clinic_membership):
        """Test updating a patient."""
        patient = Patient.objects.create(
            clinic=clinic,
            name='Update Patient',
            age=45,
            gender='M',
            phone='9998887777',
            email='update@example.com'
        )
        
        url = reverse('clinic-patient-detail', args=[clinic.id, patient.id])
        data = {
            'name': 'Updated Patient Name',
            'age': 46,
            'chief_complaint': 'Updated complaint',
            'medical_history': 'Updated history'
        }
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Updated Patient Name'
        assert response.data['age'] == 46
        assert response.data['chief_complaint'] == 'Updated complaint'
        
        # Verify the patient was updated in the database
        patient.refresh_from_db()
        assert patient.name == 'Updated Patient Name'
        assert patient.age == 46
        assert patient.chief_complaint == 'Updated complaint'
    
    def test_search_patients(self, authenticated_client, user, clinic, clinic_membership):
        """Test searching for patients."""
        Patient.objects.create(
            clinic=clinic,
            name='John Smith',
            age=30,
            gender='M',
            phone='1234567890'
        )
        Patient.objects.create(
            clinic=clinic,
            name='Jane Doe',
            age=25,
            gender='F',
            phone='0987654321'
        )
        
        # Search by name
        url = reverse('clinic-patient-list', args=[clinic.id]) + '?search=John'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'John Smith'
        
        # Search by phone
        url = reverse('clinic-patient-list', args=[clinic.id]) + '?search=09876'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Jane Doe'
    
    def test_patient_from_different_clinic(self, authenticated_client, user, clinic, clinic_membership):
        """Test that a user cannot access patients from a different clinic."""
        # Create another clinic
        other_clinic = clinic.__class__.objects.create(
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
        
        # Try to access the patient from the other clinic
        url = reverse('clinic-patient-detail', args=[clinic.id, other_patient.id])
        response = authenticated_client.get(url)
        
        # Should return 404 because the patient doesn't exist in this clinic
        assert response.status_code == status.HTTP_404_NOT_FOUND 