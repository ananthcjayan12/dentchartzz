import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from datetime import datetime
from api.models import Clinic, ClinicMembership, Patient
from api.models.dental_chart import (
    DentalCondition, DentalProcedure, DentalChartTooth, 
    DentalChartCondition, DentalChartProcedure, ChartHistory,
    GeneralProcedure
)
from django.utils import timezone
from decimal import Decimal
from rest_framework.test import APITestCase
from time import sleep

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
        # First, temporarily disable the post_save signal
        from django.db.models.signals import post_save
        from api.models.dental_chart import create_dental_chart
        post_save.disconnect(create_dental_chart, sender=Patient)
        
        # Create patient
        patient = Patient.objects.create(
            clinic=clinic,
            name='Test Patient',
            age=30,
            gender='M',
            phone='1234567890'
        )
        
        # Create permanent tooth for testing
        DentalChartTooth.objects.create(
            patient=patient,
            number='11',  # Using FDI number
            name='Upper Right Central Incisor',
            quadrant='upper_right',
            dentition_type='permanent'
        )
        
        # Create primary tooth for testing
        DentalChartTooth.objects.create(
            patient=patient,
            number='A',
            name='Upper Right Primary Second Molar',
            quadrant='upper_right',
            dentition_type='primary'
        )
        
        # Reconnect the signal
        post_save.connect(create_dental_chart, sender=Patient)
        
        return patient
    
    @pytest.fixture
    def standard_dental_conditions(self, clinic):
        """Create standard dental conditions for testing."""
        conditions = [
            {
                'name': 'Cavity',
                'code': 'C01',
                'description': 'Tooth decay or cavity',
                'color_code': '#FF0000',
                'icon': 'cavity-icon',
            },
            {
                'name': 'Fracture',
                'code': 'F01',
                'description': 'Tooth fracture or crack',
                'color_code': '#FFA500',
                'icon': 'fracture-icon',
            },
            {
                'name': 'Missing',
                'code': 'M01',
                'description': 'Missing tooth',
                'color_code': '#000000',
                'icon': 'missing-icon',
            },
            # Add more conditions to reach 10
            {
                'name': 'Impacted',
                'code': 'I01',
                'description': 'Impacted tooth',
                'color_code': '#800080',
                'icon': 'impacted-icon',
            },
            {
                'name': 'Root Canal',
                'code': 'RC01',
                'description': 'Root canal treated tooth',
                'color_code': '#0000FF',
                'icon': 'root-canal-icon',
            },
            {
                'name': 'Crown',
                'code': 'CR01',
                'description': 'Tooth with crown',
                'color_code': '#FFD700',
                'icon': 'crown-icon',
            },
            {
                'name': 'Bridge',
                'code': 'BR01',
                'description': 'Bridge abutment tooth',
                'color_code': '#A52A2A',
                'icon': 'bridge-icon',
            },
            {
                'name': 'Implant',
                'code': 'IM01',
                'description': 'Dental implant',
                'color_code': '#808080',
                'icon': 'implant-icon',
            },
            {
                'name': 'Veneer',
                'code': 'V01',
                'description': 'Tooth with veneer',
                'color_code': '#FFFFFF',
                'icon': 'veneer-icon',
            },
            {
                'name': 'Gingivitis',
                'code': 'G01',
                'description': 'Gum inflammation',
                'color_code': '#FF69B4',
                'icon': 'gingivitis-icon',
            }
        ]
        
        created_conditions = []
        for condition_data in conditions:
            condition = DentalCondition.objects.create(
                clinic=clinic,
                is_standard=True,
                **condition_data
            )
            created_conditions.append(condition)
        
        return created_conditions

    @pytest.fixture
    def standard_dental_procedures(self, clinic):
        """Create standard dental procedures for testing."""
        procedures = [
            {
                'name': 'Amalgam Filling (1 surface)',
                'code': 'D2140',
                'description': 'Silver filling for posterior teeth (1 surface)',
                'category': 'restorative',
                'default_price': 120.00,
                'duration_minutes': 30,
            },
            {
                'name': 'Composite Filling (1 surface)',
                'code': 'D2330',
                'description': 'Tooth-colored filling for anterior teeth (1 surface)',
                'category': 'restorative',
                'default_price': 150.00,
                'duration_minutes': 30,
            },
            {
                'name': 'Composite Filling (2 surfaces)',
                'code': 'D2331',
                'description': 'Tooth-colored filling for anterior teeth (2 surfaces)',
                'category': 'restorative',
                'default_price': 180.00,
                'duration_minutes': 45,
            },
            # Add more procedures to reach 10
            {
                'name': 'Root Canal - Anterior',
                'code': 'D3310',
                'description': 'Root canal therapy for anterior tooth',
                'category': 'endodontic',
                'default_price': 700.00,
                'duration_minutes': 60,
            },
            {
                'name': 'Root Canal - Premolar',
                'code': 'D3320',
                'description': 'Root canal therapy for premolar tooth',
                'category': 'endodontic',
                'default_price': 800.00,
                'duration_minutes': 75,
            },
            {
                'name': 'Root Canal - Molar',
                'code': 'D3330',
                'description': 'Root canal therapy for molar tooth',
                'category': 'endodontic',
                'default_price': 1000.00,
                'duration_minutes': 90,
            },
            {
                'name': 'Extraction - Simple',
                'code': 'D7140',
                'description': 'Simple extraction of erupted tooth',
                'category': 'oral surgery',
                'default_price': 150.00,
                'duration_minutes': 30,
            },
            {
                'name': 'Extraction - Surgical',
                'code': 'D7210',
                'description': 'Surgical extraction of erupted tooth',
                'category': 'oral surgery',
                'default_price': 250.00,
                'duration_minutes': 45,
            },
            {
                'name': 'Crown - Porcelain/Ceramic',
                'code': 'D2740',
                'description': 'Porcelain/ceramic crown',
                'category': 'prosthodontic',
                'default_price': 1200.00,
                'duration_minutes': 60,
            },
            {
                'name': 'Scaling and Root Planing (per quadrant)',
                'code': 'D4341',
                'description': 'Deep cleaning for periodontal disease',
                'category': 'periodontic',
                'default_price': 200.00,
                'duration_minutes': 45,
            }
        ]
        
        created_procedures = []
        for procedure_data in procedures:
            procedure = DentalProcedure.objects.create(
                clinic=clinic,
                is_standard=True,
                **procedure_data
            )
            created_procedures.append(procedure)
        
        return created_procedures
    
    @pytest.fixture
    def clinic_membership(self, user, clinic):
        """Create clinic membership for test user."""
        membership = ClinicMembership.objects.create(
            user=user,
            clinic=clinic,
            role='administrator'
        )
        return membership

    def test_get_dental_conditions(self, authenticated_client, user, clinic, clinic_membership, dental_condition):
        """Test getting dental conditions."""
        url = reverse('dental-conditions', kwargs={'clinic_id': clinic.id})
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
        """Test retrieving a dental chart."""
        url = reverse('dental-chart', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient_with_teeth.id
        })
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['patient_id'] == patient_with_teeth.id
        assert response.data['patient_name'] == patient_with_teeth.name
        
        # Check permanent teeth
        assert len(response.data['permanent_teeth']) == 1
        permanent_tooth = response.data['permanent_teeth'][0]
        assert permanent_tooth['number'] == '11'
        assert permanent_tooth['dentition_type'] == 'permanent'
        
        # Check primary teeth
        assert len(response.data['primary_teeth']) == 1
        primary_tooth = response.data['primary_teeth'][0]
        assert primary_tooth['number'] == 'A'
        assert primary_tooth['dentition_type'] == 'primary'
    
    def test_add_tooth_condition_to_permanent_tooth(self, authenticated_client, patient_with_teeth, dental_condition, clinic_membership):
        """Test adding a condition to a permanent tooth."""
        url = reverse('add-tooth-condition', kwargs={
            'clinic_id': patient_with_teeth.clinic.id,
            'patient_id': patient_with_teeth.id,
            'tooth_number': '11'
        })
        data = {
            'condition_id': dental_condition.id,
            'surface': 'mesial',
            'description': 'Test condition',
            'severity': 'moderate',
            'dentition_type': 'permanent'
        }
        
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_add_tooth_condition_to_primary_tooth(self, authenticated_client, patient_with_teeth, dental_condition, clinic_membership):
        """Test adding a condition to a primary tooth."""
        url = reverse('add-tooth-condition', kwargs={
            'clinic_id': patient_with_teeth.clinic.id,
            'patient_id': patient_with_teeth.id,
            'tooth_number': 'A'
        })
        data = {
            'condition_id': dental_condition.id,
            'surface': 'mesial',
            'description': 'Test condition',
            'severity': 'moderate'
        }
        
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_add_procedure_to_primary_tooth(self, authenticated_client, user, clinic, 
                                          clinic_membership, patient_with_teeth, dental_procedure):
        """Test adding a procedure to a primary tooth."""
        url = reverse('add-tooth-procedure', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient_with_teeth.id,
            'tooth_number': 'A'
        })
        data = {
            'procedure_id': dental_procedure.id,
            'surface': 'occlusal',
            'notes': 'Primary tooth procedure',
            'date_performed': '2023-11-21',
            'price': 100.00,
            'status': 'completed'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['procedure_id'] == dental_procedure.id
        assert response.data['surface'] == 'occlusal'
        assert float(response.data['price']) == 100.00
    
    def test_invalid_tooth_number_format(self, authenticated_client, user, clinic, 
                                       clinic_membership, patient_with_teeth, dental_condition):
        """Test adding a condition with invalid tooth number format."""
        url = reverse('add-tooth-condition', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient_with_teeth.id,
            'tooth_number': 'X'
        })
        data = {
            'condition_id': dental_condition.id,
            'surface': 'occlusal',
            'notes': 'Test note',
            'severity': 'moderate'
        }
        
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_dentition_type_mismatch(self, authenticated_client, user, clinic,
                                   clinic_membership, patient_with_teeth, dental_condition):
        """Test adding a condition with mismatched dentition type."""
        url = reverse('add-tooth-condition', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient_with_teeth.id,
            'tooth_number': '11'  # Using FDI number that exists
        })
        data = {
            'condition_id': dental_condition.id,
            'surface': 'occlusal',
            'description': 'Test note',
            'severity': 'moderate',
            'dentition_type': 'primary'  # Mismatch with permanent tooth
        }
        
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_tooth_procedure(self, authenticated_client, user, clinic, clinic_membership,
                                patient_with_teeth, dental_procedure):
        """Test adding a procedure to a tooth."""
        url = reverse('add-tooth-procedure', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient_with_teeth.id,
            'tooth_number': '11'  # Using FDI number
        })
        data = {
            'procedure_id': dental_procedure.id,
            'surface': 'occlusal',
            'description': 'Amalgam filling',  # Changed from notes
            'date_performed': '2023-11-21',
            'price': 120.00,
            'status': 'completed'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['procedure_id'] == dental_procedure.id
        assert response.data['surface'] == 'occlusal'
        assert response.data['description'] == 'Amalgam filling'
        assert float(response.data['price']) == 120.00
        assert response.data['status'] == 'completed'
        
        # Check that the procedure was added to the tooth
        tooth = DentalChartTooth.objects.get(
            patient=patient_with_teeth, 
            number='11',
            dentition_type='permanent'
        )
        assert tooth.procedures.count() == 1
        
        # Check that a history entry was created
        history = ChartHistory.objects.filter(patient=patient_with_teeth)
        assert history.count() == 1
        assert history.first().action == 'add_procedure'
        assert history.first().tooth_number == '11'
    
    def test_update_tooth_condition(self, authenticated_client, user, clinic, clinic_membership,
                                   patient_with_teeth, dental_condition):
        """Test updating a condition on a tooth."""
        tooth = DentalChartTooth.objects.get(
            patient=patient_with_teeth,
            number='11',
            dentition_type='permanent'
        )
        condition = DentalChartCondition.objects.create(
            tooth=tooth,
            condition=dental_condition,
            surface='occlusal',
            description='Initial notes',
            severity='mild',
            created_by=user,
            updated_by=user
        )
        
        url = reverse('tooth-condition-detail', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient_with_teeth.id,
            'tooth_number': '11',
            'condition_id': condition.id
        })
        data = {
            'surface': 'occlusal,buccal',
            'description': 'Updated notes',
            'severity': 'severe'
        }
        
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['surface'] == 'occlusal,buccal'
        assert response.data['description'] == 'Updated notes'
        
        # Check that the condition was updated
        condition.refresh_from_db()
        assert condition.surface == 'occlusal,buccal'
        assert condition.description == 'Updated notes'
        assert condition.severity == 'severe'
        
        # Check that a history entry was created
        history = ChartHistory.objects.filter(patient=patient_with_teeth, action='update_condition')
        assert history.count() == 1
    
    def test_delete_tooth_condition(self, authenticated_client, user, clinic, clinic_membership, 
                                   patient_with_teeth, dental_condition):
        """Test deleting a condition from a tooth."""
        # First add a condition
        tooth = DentalChartTooth.objects.get(patient=patient_with_teeth, number=11)
        condition = DentalChartCondition.objects.create(
            tooth=tooth,
            condition=dental_condition,
            surface='occlusal',
            description='Test notes',
            severity='moderate',
            created_by=user,
            updated_by=user
        )
        
        # Now delete it
        url = reverse('tooth-condition-detail', args=[clinic.id, patient_with_teeth.id, 11, condition.id])
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
            tooth_number=11,
            details={'condition_name': 'Cavity', 'surface': 'occlusal'}
        )
        
        ChartHistory.objects.create(
            patient=patient_with_teeth,
            user=user,
            action='add_procedure',
            tooth_number=11,
            details={'procedure_name': 'Filling', 'surface': 'occlusal'}
        )
        
        url = reverse('dental-chart-history', args=[clinic.id, patient_with_teeth.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2  # Check count in paginated response
        assert len(response.data['results']) == 2  # Check results in paginated response

    def test_create_custom_dental_condition(self, authenticated_client, user, clinic, clinic_membership):
        """Test creating a custom dental condition."""
        url = reverse('dental-conditions', args=[clinic.id])
        data = {
            'name': 'Severe Enamel Hypoplasia',
            'code': 'SEH01',
            'description': 'Developmental defect of enamel',
            'color_code': '#8A2BE2'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Severe Enamel Hypoplasia'
        assert response.data['code'] == 'SEH01'
        assert response.data['is_standard'] == False
        
        # Verify it was added to the database
        condition = DentalCondition.objects.get(id=response.data['id'])
        assert condition.clinic == clinic
        assert condition.name == 'Severe Enamel Hypoplasia'

    def test_create_custom_dental_procedure(self, authenticated_client, user, clinic, clinic_membership):
        """Test creating a custom dental procedure."""
        url = reverse('dental-procedures', args=[clinic.id])
        data = {
            'name': 'Microscopic Root Canal',
            'code': 'MRC01',
            'description': 'Root canal treatment using dental microscope',
            'default_price': 950.00
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Microscopic Root Canal'
        assert response.data['code'] == 'MRC01'
        assert response.data['default_price'] == '950.00'
        assert response.data['is_standard'] == False
        
        # Verify it was added to the database
        procedure = DentalProcedure.objects.get(id=response.data['id'])
        assert procedure.clinic == clinic
        assert procedure.name == 'Microscopic Root Canal'

    def test_add_tooth_condition_with_custom_condition(self, authenticated_client, user, clinic,
                                                      clinic_membership, patient_with_teeth):
        """Test adding a custom condition to a tooth."""
        url = reverse('add-tooth-condition', args=[clinic.id, patient_with_teeth.id, '11'])
        data = {
            'custom_name': 'Unusual Discoloration',
            'custom_code': 'UD01',
            'custom_description': 'Unusual discoloration not matching standard conditions',
            'surface': 'labial',
            'description': 'Patient reports no pain but concerned about appearance',
            'severity': 'mild'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['surface'] == 'labial'
        assert response.data['description'] == 'Patient reports no pain but concerned about appearance'
        assert response.data['severity'] == 'mild'
        assert response.data['condition_name'] == 'Unusual Discoloration'
        assert response.data['condition_code'] == 'UD01'
        
        # Check that a new condition was created
        condition = DentalCondition.objects.filter(name='Unusual Discoloration').first()
        assert condition is not None
        assert condition.is_standard == False
        
        # Check that the condition was added to the tooth
        tooth = DentalChartTooth.objects.get(patient=patient_with_teeth, number=11)
        assert tooth.conditions.count() == 1
        
        # Check that a history entry was created
        history = ChartHistory.objects.filter(patient=patient_with_teeth)
        assert history.count() == 1
        assert history.first().action == 'add_condition'
        assert history.first().tooth_number == '11'

    def test_add_tooth_procedure_with_custom_procedure(self, authenticated_client, user, clinic,
                                                      clinic_membership, patient_with_teeth):
        """Test adding a custom procedure to a tooth."""
        url = reverse('add-tooth-procedure', args=[clinic.id, patient_with_teeth.id, '11'])
        data = {
            'custom_name': 'Specialized Veneer Technique',
            'custom_code': 'SVT01',
            'custom_description': 'Specialized minimal-prep veneer technique',
            'surface': 'labial',
            'description': 'Used new material for better aesthetics',
            'date_performed': '2023-12-01',
            'price': 850.00,
            'status': 'completed'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['surface'] == 'labial'
        assert response.data['description'] == 'Used new material for better aesthetics'
        assert response.data['price'] == '850.00'
        assert response.data['status'] == 'completed'
        assert response.data['procedure_name'] == 'Specialized Veneer Technique'
        assert response.data['procedure_code'] == 'SVT01'
        
        # Check that a new procedure was created
        procedure = DentalProcedure.objects.filter(name='Specialized Veneer Technique').first()
        assert procedure is not None
        assert procedure.is_standard == False
        
        # Check that the procedure was added to the tooth
        tooth = DentalChartTooth.objects.get(patient=patient_with_teeth, number=11)
        assert tooth.procedures.count() == 1
        
        # Check that a history entry was created
        history = ChartHistory.objects.filter(patient=patient_with_teeth)
        assert history.count() == 1
        assert history.first().action == 'add_procedure'
        assert history.first().tooth_number == '11'

    def test_standard_dental_conditions_exist(self, authenticated_client, user, clinic, 
                                             clinic_membership, standard_dental_conditions):
        """Test that standard dental conditions exist after migrations."""
        url = reverse('dental-conditions', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Should have at least the 10 standard conditions
        assert len(response.data['results']) >= 10
        
        # Check for specific standard conditions
        condition_names = [condition['name'] for condition in response.data['results']]
        assert 'Cavity' in condition_names
        assert 'Fracture' in condition_names
        assert 'Missing' in condition_names
        
        # Verify they are marked as standard
        standard_conditions = [c for c in response.data['results'] if c['is_standard']]
        assert len(standard_conditions) >= 10

    def test_standard_dental_procedures_exist(self, authenticated_client, user, clinic, 
                                             clinic_membership, standard_dental_procedures):
        """Test that standard dental procedures exist after migrations."""
        url = reverse('dental-procedures', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Should have at least the 10 standard procedures
        assert len(response.data['results']) >= 10
        
        # Check for specific standard procedures
        procedure_names = [proc['name'] for proc in response.data['results']]
        assert 'Amalgam Filling (1 surface)' in procedure_names
        assert 'Root Canal - Molar' in procedure_names
        assert 'Extraction - Simple' in procedure_names
        
        # Verify they are marked as standard
        standard_procedures = [p for p in response.data['results'] if p['is_standard']]
        assert len(standard_procedures) >= 10

    def test_add_tooth_condition_with_standard_condition(self, authenticated_client, user, clinic,
                                                       clinic_membership, patient_with_teeth,
                                                       standard_dental_conditions):
        """Test adding a standard condition to a tooth."""
        conditions_url = reverse('dental-conditions', args=[clinic.id])
        conditions_response = authenticated_client.get(conditions_url)
        assert conditions_response.status_code == status.HTTP_200_OK
        
        standard_condition = next(c for c in conditions_response.data['results'] if c['is_standard'])
        
        url = reverse('add-tooth-condition', args=[clinic.id, patient_with_teeth.id, '11'])
        data = {
            'condition_id': standard_condition['id'],
            'surface': 'occlusal',
            'description': 'Using standard condition',
            'severity': 'moderate'
        }
        
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['condition_id'] == standard_condition['id']
        assert response.data['condition_name'] == standard_condition['name']
        assert response.data['surface'] == 'occlusal'
        assert response.data['description'] == 'Using standard condition'

    def test_add_tooth_procedure_with_standard_procedure(self, authenticated_client, user, clinic,
                                                       clinic_membership, patient_with_teeth,
                                                       standard_dental_procedures):
        """Test adding a standard procedure to a tooth."""
        procedures_url = reverse('dental-procedures', args=[clinic.id])
        procedures_response = authenticated_client.get(procedures_url)
        assert procedures_response.status_code == status.HTTP_200_OK
        
        standard_procedure = next(p for p in procedures_response.data['results'] if p['is_standard'])
        
        url = reverse('add-tooth-procedure', args=[clinic.id, patient_with_teeth.id, '11'])
        data = {
            'procedure_id': standard_procedure['id'],
            'surface': 'occlusal',
            'description': 'Using standard procedure',
            'date_performed': '2023-12-01',
            'price': standard_procedure['default_price'],
            'status': 'completed'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['procedure_name'] == standard_procedure['name']
        assert response.data['surface'] == 'occlusal'
        assert response.data['description'] == 'Using standard procedure'

    def test_filter_dental_conditions_by_name(self, authenticated_client, user, clinic, 
                                             clinic_membership, standard_dental_conditions):
        """Test filtering dental conditions by name."""
        url = reverse('dental-conditions', args=[clinic.id]) + '?search=cavity'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
        for condition in response.data['results']:
            assert 'cavity' in condition['name'].lower() or 'cavity' in condition['description'].lower()

    def test_filter_dental_procedures_by_category(self, authenticated_client, user, clinic, 
                                                 clinic_membership, standard_dental_procedures):
        """Test filtering dental procedures by category."""
        url = reverse('dental-procedures', args=[clinic.id]) + '?category=restorative'
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) > 0
        for procedure in response.data['results']:
            assert procedure['category'] == 'restorative'

    def test_add_condition_to_patient_without_teeth(self, authenticated_client, user, clinic,
                                                  clinic_membership, dental_condition):
        """Test adding a condition to a patient who doesn't have teeth records yet."""
        # Create a new patient (teeth will be created automatically)
        patient = Patient.objects.create(
            clinic=clinic,
            name='New Patient',
            age=25,
            gender='F',
            phone='9876543210'
        )
        
        # Try to add a condition using FDI number
        url = reverse('add-tooth-condition', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient.id,
            'tooth_number': '11'  # Using FDI number
        })
        data = {
            'condition_id': dental_condition.id,
            'surface': 'mesial',
            'description': 'Test condition',  # Changed from notes to description
            'severity': 'moderate',
            'dentition_type': 'permanent'
        }
        
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_dental_chart_includes_conditions_and_procedures(self, authenticated_client, user, clinic, 
                                                       clinic_membership, patient_with_teeth, 
                                                       dental_condition, dental_procedure):
        """Test that the dental chart endpoint returns teeth with their conditions and procedures."""
        # Add a condition to a tooth
        tooth = DentalChartTooth.objects.get(
            patient=patient_with_teeth, 
            number='11',
            dentition_type='permanent'
        )
        
        # Add a condition
        condition = DentalChartCondition.objects.create(
            tooth=tooth,
            condition=dental_condition,
            surface='occlusal',
            description='Initial notes',
            severity='mild',
            created_by=user,
            updated_by=user
        )
        
        # Add a procedure
        procedure = DentalChartProcedure.objects.create(
            tooth=tooth,
            procedure=dental_procedure,
            surface='occlusal',
            description='Initial procedure',
            date_performed=timezone.now(),
            performed_by=user,
            price=100.00,
            status='completed'
        )
        
        # Get the dental chart
        url = reverse('dental-chart', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient_with_teeth.id
        })
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Find the tooth in the response
        permanent_teeth = response.data['permanent_teeth']
        tooth_data = next(t for t in permanent_teeth if t['number'] == '11')
        
        # Check that the tooth has conditions
        assert 'conditions' in tooth_data
        assert len(tooth_data['conditions']) == 1
        condition_data = tooth_data['conditions'][0]
        assert condition_data['condition_id'] == dental_condition.id
        assert condition_data['condition_name'] == dental_condition.name
        assert condition_data['condition_code'] == dental_condition.code
        assert condition_data['surface'] == 'occlusal'
        assert condition_data['description'] == 'Initial notes'
        assert condition_data['severity'] == 'mild'
        assert condition_data['created_by'] == user.get_full_name()
        
        # Check that the tooth has procedures
        assert 'procedures' in tooth_data
        assert len(tooth_data['procedures']) == 1
        procedure_data = tooth_data['procedures'][0]
        assert procedure_data['procedure_id'] == dental_procedure.id
        assert procedure_data['procedure_name'] == dental_procedure.name
        assert procedure_data['procedure_code'] == dental_procedure.code
        assert procedure_data['surface'] == 'occlusal'
        assert procedure_data['description'] == 'Initial procedure'
        assert procedure_data['price'] == '100.00'
        assert procedure_data['status'] == 'completed'
        assert procedure_data['performed_by'] == user.get_full_name()

    def test_update_tooth_procedure(self, authenticated_client, user, clinic, 
                                  clinic_membership, patient_with_teeth, dental_procedure):
        """Test updating a procedure on a tooth."""
        tooth = DentalChartTooth.objects.get(
            patient=patient_with_teeth,
            number='11',
            dentition_type='permanent'
        )
        
        procedure = DentalChartProcedure.objects.create(
            tooth=tooth,
            procedure=dental_procedure,
            surface='occlusal',
            description='Initial procedure',
            date_performed=timezone.now(),
            performed_by=user,
            price=100.00,
            status='in_progress'
        )
        
        url = reverse('tooth-procedure-detail', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient_with_teeth.id,
            'tooth_number': '11',
            'procedure_id': procedure.id
        })
        
        update_data = {
            'surface': 'mesial,distal',
            'description': 'Updated procedure notes',
            'date_performed': '2024-01-15',
            'price': 150.00,
            'status': 'completed'
        }
        
        response = authenticated_client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['surface'] == 'mesial,distal'
        assert response.data['description'] == 'Updated procedure notes'

    def test_delete_tooth_procedure(self, authenticated_client, user, clinic, 
                                  clinic_membership, patient_with_teeth, dental_procedure):
        """Test deleting a procedure from a tooth."""
        # First create a procedure
        tooth = DentalChartTooth.objects.get(
            patient=patient_with_teeth,
            number='11',
            dentition_type='permanent'
        )
        
        procedure = DentalChartProcedure.objects.create(
            tooth=tooth,
            procedure=dental_procedure,
            surface='occlusal',
            description='Initial procedure',
            date_performed=timezone.now(),
            performed_by=user,
            price=100.00,
            status='in_progress'
        )
        
        # Delete the procedure
        url = reverse('tooth-procedure-detail', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient_with_teeth.id,
            'tooth_number': '11',
            'procedure_id': procedure.id
        })
        
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the procedure was deleted
        assert not DentalChartProcedure.objects.filter(id=procedure.id).exists()
        
        # Verify history was created
        history = ChartHistory.objects.filter(
            patient=patient_with_teeth,
            action='remove_procedure'
        ).latest('date')
        assert history.tooth_number == '11'
        assert history.details['procedure_name'] == dental_procedure.name
        assert float(history.details['price']) == 100.00
        assert history.details['status'] == 'in_progress'

    def test_add_procedure_note(self, authenticated_client, user, clinic, 
                              clinic_membership, patient_with_teeth, dental_procedure):
        """Test adding a note to a procedure."""
        # First create a procedure
        tooth = DentalChartTooth.objects.get(
            patient=patient_with_teeth,
            number='11',
            dentition_type='permanent'
        )
        
        # Update the user to have a first and last name
        user.first_name = "Test"
        user.last_name = "User"
        user.save()
        
        procedure = DentalChartProcedure.objects.create(
            tooth=tooth,
            procedure=dental_procedure,
            surface='occlusal',
            description='Initial procedure',
            date_performed=timezone.now(),
            performed_by=user,
            price=100.00,
            status='in_progress'
        )
        
        # Add a note
        url = reverse('add-procedure-note', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient_with_teeth.id,
            'tooth_number': '11',
            'procedure_id': procedure.id
        })
        
        note_data = {
            'note': 'Progress note for the procedure',
            'appointment_date': timezone.now().strftime('%Y-%m-%d %H:%M')
        }
        
        response = authenticated_client.post(url, note_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['note'] == note_data['note']
        assert response.data['created_by'] == "Test User"  # Now should match the full name
        
        # Verify history was created
        history = ChartHistory.objects.filter(
            patient=patient_with_teeth,
            action='add_procedure_note'
        ).latest('date')
        assert history.tooth_number == '11'
        assert history.category == 'procedures'
        assert history.details['note'] == note_data['note']

    def test_get_chart_history_with_filters(self, authenticated_client, user, clinic,
                                          clinic_membership, patient_with_teeth):
        """Test getting chart history with various filters."""
        # Create some history entries
        ChartHistory.objects.create(
            patient=patient_with_teeth,
            user=user,
            action='add_procedure',
            tooth_number='11',
            category='procedures',
            details={'procedure_name': 'Test Procedure'}
        )
        
        ChartHistory.objects.create(
            patient=patient_with_teeth,
            user=user,
            action='add_condition',
            tooth_number='2',
            category='conditions',
            details={'condition_name': 'Test Condition'}
        )
        
        # Test filtering by tooth number
        url = reverse('dental-chart-history', kwargs={
            'clinic_id': clinic.id,
            'patient_id': patient_with_teeth.id
        }) + '?tooth_number=11'
        
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1  # Check count in paginated response
        assert len(response.data['results']) == 1  # Check results in paginated response
        assert response.data['results'][0]['tooth_number'] == '11'

class GeneralProcedureTests(APITestCase):
    def setUp(self):
        # Create test clinic
        self.clinic = Clinic.objects.create(name="Test Clinic")
        
        # Create test user (dentist)
        self.user = User.objects.create_user(
            username='testdentist',
            password='testpass123',
            first_name='Test',
            last_name='Dentist'
        )
        
        # Create clinic membership
        self.membership = ClinicMembership.objects.create(
            user=self.user,
            clinic=self.clinic,
            role='dentist'
        )
        
        # Create test patient
        self.patient = Patient.objects.create(
            name="Test Patient",
            clinic=self.clinic,
            age=30,
            gender='M'
        )
        
        # Create test dental procedure
        self.procedure = DentalProcedure.objects.create(
            clinic=self.clinic,
            name="Scaling and Polishing",
            code="D1110",
            description="Full mouth scaling and polishing",
            default_price=Decimal('150.00')
        )
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
        
    def test_add_general_procedure(self):
        """Test adding a general procedure."""
        url = reverse('general-procedures', kwargs={
            'clinic_id': self.clinic.id,
            'patient_id': self.patient.id
        })
        
        data = {
            'procedure_id': self.procedure.id,
            'notes': "General scaling and polishing done",
            'date_performed': "2024-03-19",
            'price': "150.00",
            'status': "completed"
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['procedure_name'], "Scaling and Polishing")
        self.assertEqual(response.data['procedure_code'], "D1110")
        self.assertEqual(response.data['notes'], "General scaling and polishing done")
        self.assertEqual(response.data['status'], "completed")
        self.assertEqual(Decimal(response.data['price']), Decimal('150.00'))
        self.assertEqual(response.data['performed_by'], "Test Dentist")
    
    def test_list_general_procedures(self):
        """Test listing general procedures."""
        # Create first procedure
        GeneralProcedure.objects.create(
            clinic=self.clinic,
            patient=self.patient,
            procedure=self.procedure,
            dentist=self.user,
            notes="First procedure",
            date_performed=timezone.now().date(),
            price=Decimal('150.00'),
            status='completed'
        )
        
        # Add a small delay to ensure different created_at times
        sleep(0.1)
        
        # Create second procedure
        GeneralProcedure.objects.create(
            clinic=self.clinic,
            patient=self.patient,
            procedure=self.procedure,
            dentist=self.user,
            notes="Second procedure",
            date_performed=timezone.now().date(),
            price=Decimal('150.00'),
            status='planned'
        )
        
        url = reverse('general-procedures', kwargs={
            'clinic_id': self.clinic.id,
            'patient_id': self.patient.id
        })
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check paginated response
        self.assertEqual(len(response.data['results']), 2)  # Check results count
        self.assertEqual(response.data['count'], 2)  # Check total count
        self.assertEqual(response.data['results'][0]['notes'], "Second procedure")  # Most recent first
        self.assertEqual(response.data['results'][1]['notes'], "First procedure")  # Older second
    
    def test_add_general_procedure_invalid_data(self):
        """Test adding a general procedure with invalid data."""
        url = reverse('general-procedures', kwargs={
            'clinic_id': self.clinic.id,
            'patient_id': self.patient.id
        })
        
        # Missing required field procedure_id
        data = {
            'notes': "General scaling and polishing done",
            'date_performed': "2024-03-19",
            'price': "150.00",
            'status': "completed"
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('procedure_id', response.data['details'])
    
    def test_add_general_procedure_invalid_procedure(self):
        """Test adding a general procedure with invalid procedure ID."""
        url = reverse('general-procedures', kwargs={
            'clinic_id': self.clinic.id,
            'patient_id': self.patient.id
        })
        
        data = {
            'procedure_id': 99999,  # Non-existent procedure ID
            'notes': "General scaling and polishing done",
            'date_performed': "2024-03-19",
            'price': "150.00",
            'status': "completed"
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_add_general_procedure_invalid_patient(self):
        """Test adding a general procedure for invalid patient."""
        url = reverse('general-procedures', kwargs={
            'clinic_id': self.clinic.id,
            'patient_id': 99999  # Non-existent patient ID
        })
        
        data = {
            'procedure_id': self.procedure.id,
            'notes': "General scaling and polishing done",
            'date_performed': "2024-03-19",
            'price': "150.00",
            'status': "completed"
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 