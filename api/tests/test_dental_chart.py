import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from datetime import datetime
from api.models import Clinic, ClinicMembership, Patient
from api.models.dental_chart import (
    DentalCondition, DentalProcedure, DentalChartTooth, 
    DentalChartCondition, DentalChartProcedure, ChartHistory
)

@pytest.mark.django_db
class TestDentalChartEndpoints:
    """Test dental chart endpoints."""
    
    @pytest.fixture
    def dental_condition(self, clinic):
        """Create and return a test dental condition."""
        return DentalCondition.objects.create(
            clinic=clinic,
            name='Cavity',
            code='CAV',
            description='Tooth decay or cavity',
            color_code='#FF0000',
            icon='cavity-icon'
        )
    
    @pytest.fixture
    def dental_procedure(self, clinic):
        """Create and return a test dental procedure."""
        return DentalProcedure.objects.create(
            clinic=clinic,
            name='Amalgam Filling',
            code='D2140',
            description='Amalgam filling - one surface',
            category='restorative',
            default_price=120.00,
            duration_minutes=30
        )
    
    @pytest.fixture
    def patient_with_teeth(self, clinic):
        """Create and return a patient with teeth."""
        patient = Patient.objects.create(
            clinic=clinic,
            name='Test Patient',
            age=30,
            gender='M',
            phone='1234567890'
        )
        
        # Create a tooth for testing
        DentalChartTooth.objects.create(
            patient=patient,
            number=1,
            name='Upper Right Third Molar',
            quadrant='upper_right',
            type='molar'
        )
        
        return patient
    
    def test_get_dental_conditions(self, authenticated_client, user, clinic, clinic_membership, dental_condition):
        """Test getting dental conditions."""
        url = reverse('dental-conditions', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Cavity'
        assert response.data['results'][0]['code'] == 'CAV'
    
    def test_get_dental_procedures(self, authenticated_client, user, clinic, clinic_membership, dental_procedure):
        """Test getting dental procedures."""
        url = reverse('dental-procedures', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Amalgam Filling'
        assert response.data['results'][0]['code'] == 'D2140'
    
    def test_get_dental_chart(self, authenticated_client, user, clinic, clinic_membership, patient_with_teeth):
        """Test getting a patient's dental chart."""
        url = reverse('dental-chart', args=[clinic.id, patient_with_teeth.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == patient_with_teeth.id
        assert response.data['patient_name'] == patient_with_teeth.name
        assert len(response.data['teeth']) == 1
        assert response.data['teeth'][0]['number'] == 1
        assert response.data['teeth'][0]['name'] == 'Upper Right Third Molar'
    
    def test_add_tooth_condition(self, authenticated_client, user, clinic, clinic_membership, 
                                patient_with_teeth, dental_condition):
        """Test adding a condition to a tooth."""
        url = reverse('add-tooth-condition', args=[clinic.id, patient_with_teeth.id, 1])
        data = {
            'condition_id': dental_condition.id,
            'surface': 'occlusal',
            'notes': 'Deep cavity on occlusal surface',
            'severity': 'moderate'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['condition_id'] == dental_condition.id
        assert response.data['surface'] == 'occlusal'
        assert response.data['notes'] == 'Deep cavity on occlusal surface'
        assert response.data['severity'] == 'moderate'
        
        # Check that the condition was added to the tooth
        tooth = DentalChartTooth.objects.get(patient=patient_with_teeth, number=1)
        assert tooth.conditions.count() == 1
        
        # Check that a history entry was created
        history = ChartHistory.objects.filter(patient=patient_with_teeth)
        assert history.count() == 1
        assert history.first().action == 'add_condition'
        assert history.first().tooth_number == 1
    
    def test_add_tooth_procedure(self, authenticated_client, user, clinic, clinic_membership, 
                                patient_with_teeth, dental_procedure):
        """Test adding a procedure to a tooth."""
        url = reverse('add-tooth-procedure', args=[clinic.id, patient_with_teeth.id, 1])
        data = {
            'procedure_id': dental_procedure.id,
            'surface': 'occlusal',
            'notes': 'Amalgam filling',
            'date_performed': '2023-11-21',
            'price': 120.00,
            'status': 'completed'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['procedure_id'] == dental_procedure.id
        assert response.data['surface'] == 'occlusal'
        assert response.data['notes'] == 'Amalgam filling'
        assert response.data['price'] == '120.00'
        assert response.data['status'] == 'completed'
        
        # Check that the procedure was added to the tooth
        tooth = DentalChartTooth.objects.get(patient=patient_with_teeth, number=1)
        assert tooth.procedures.count() == 1
        
        # Check that a history entry was created
        history = ChartHistory.objects.filter(patient=patient_with_teeth)
        assert history.count() == 1
        assert history.first().action == 'add_procedure'
        assert history.first().tooth_number == 1
    
    def test_update_tooth_condition(self, authenticated_client, user, clinic, clinic_membership, 
                                   patient_with_teeth, dental_condition):
        """Test updating a condition on a tooth."""
        # First add a condition
        tooth = DentalChartTooth.objects.get(patient=patient_with_teeth, number=1)
        condition = DentalChartCondition.objects.create(
            tooth=tooth,
            condition=dental_condition,
            surface='occlusal',
            notes='Initial notes',
            severity='mild',
            created_by=user,
            updated_by=user
        )
        
        # Now update it
        url = reverse('tooth-condition-detail', args=[clinic.id, patient_with_teeth.id, 1, condition.id])
        data = {
            'surface': 'occlusal,buccal',
            'notes': 'Updated notes',
            'severity': 'severe'
        }
        
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['surface'] == 'occlusal,buccal'
        assert response.data['notes'] == 'Updated notes'
        assert response.data['severity'] == 'severe'
        
        # Check that the condition was updated
        condition.refresh_from_db()
        assert condition.surface == 'occlusal,buccal'
        assert condition.notes == 'Updated notes'
        assert condition.severity == 'severe'
        
        # Check that a history entry was created
        history = ChartHistory.objects.filter(patient=patient_with_teeth, action='update_condition')
        assert history.count() == 1
    
    def test_delete_tooth_condition(self, authenticated_client, user, clinic, clinic_membership, 
                                   patient_with_teeth, dental_condition):
        """Test deleting a condition from a tooth."""
        # First add a condition
        tooth = DentalChartTooth.objects.get(patient=patient_with_teeth, number=1)
        condition = DentalChartCondition.objects.create(
            tooth=tooth,
            condition=dental_condition,
            surface='occlusal',
            notes='Test notes',
            severity='moderate',
            created_by=user,
            updated_by=user
        )
        
        # Now delete it
        url = reverse('tooth-condition-detail', args=[clinic.id, patient_with_teeth.id, 1, condition.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Check that the condition was deleted
        assert not DentalChartCondition.objects.filter(id=condition.id).exists()
        
        # Check that a history entry was created
        history = ChartHistory.objects.filter(patient=patient_with_teeth, action='remove_condition')
        assert history.count() == 1
    
    def test_get_chart_history(self, authenticated_client, user, clinic, clinic_membership, patient_with_teeth):
        """Test getting the history of a patient's dental chart."""
        # Create some history entries
        ChartHistory.objects.create(
            patient=patient_with_teeth,
            user=user,
            action='add_condition',
            tooth_number=1,
            details={'condition_name': 'Cavity', 'surface': 'occlusal'}
        )
        
        ChartHistory.objects.create(
            patient=patient_with_teeth,
            user=user,
            action='add_procedure',
            tooth_number=1,
            details={'procedure_name': 'Filling', 'surface': 'occlusal'}
        )
        
        url = reverse('dental-chart-history', args=[clinic.id, patient_with_teeth.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Check that the history entries are in the correct order (newest first)
        assert response.data['results'][0]['action'] == 'add_procedure'
        assert response.data['results'][1]['action'] == 'add_condition' 