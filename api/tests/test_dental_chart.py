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
        url = reverse('add-tooth-condition', args=[clinic.id, patient_with_teeth.id, 1])
        data = {
            'custom_name': 'Unusual Discoloration',
            'custom_code': 'UD01',
            'custom_description': 'Unusual discoloration not matching standard conditions',
            'surface': 'labial',
            'notes': 'Patient reports no pain but concerned about appearance',
            'severity': 'mild'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['surface'] == 'labial'
        assert response.data['notes'] == 'Patient reports no pain but concerned about appearance'
        assert response.data['severity'] == 'mild'
        assert response.data['condition_name'] == 'Unusual Discoloration'
        assert response.data['condition_code'] == 'UD01'
        
        # Check that a new condition was created
        condition = DentalCondition.objects.filter(name='Unusual Discoloration').first()
        assert condition is not None
        assert condition.is_standard == False
        
        # Check that the condition was added to the tooth
        tooth = DentalChartTooth.objects.get(patient=patient_with_teeth, number=1)
        assert tooth.conditions.count() == 1
        
        # Check that a history entry was created
        history = ChartHistory.objects.filter(patient=patient_with_teeth)
        assert history.count() == 1
        assert history.first().action == 'add_condition'
        assert history.first().tooth_number == 1

    def test_add_tooth_procedure_with_custom_procedure(self, authenticated_client, user, clinic, 
                                                      clinic_membership, patient_with_teeth):
        """Test adding a custom procedure to a tooth."""
        url = reverse('add-tooth-procedure', args=[clinic.id, patient_with_teeth.id, 1])
        data = {
            'custom_name': 'Specialized Veneer Technique',
            'custom_code': 'SVT01',
            'custom_description': 'Specialized minimal-prep veneer technique',
            'surface': 'labial',
            'notes': 'Used new material for better aesthetics',
            'date_performed': '2023-12-01',
            'price': 850.00,
            'status': 'completed'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['surface'] == 'labial'
        assert response.data['notes'] == 'Used new material for better aesthetics'
        assert response.data['price'] == '850.00'
        assert response.data['status'] == 'completed'
        assert response.data['procedure_name'] == 'Specialized Veneer Technique'
        assert response.data['procedure_code'] == 'SVT01'
        
        # Check that a new procedure was created
        procedure = DentalProcedure.objects.filter(name='Specialized Veneer Technique').first()
        assert procedure is not None
        assert procedure.is_standard == False
        
        # Check that the procedure was added to the tooth
        tooth = DentalChartTooth.objects.get(patient=patient_with_teeth, number=1)
        assert tooth.procedures.count() == 1
        
        # Check that a history entry was created
        history = ChartHistory.objects.filter(patient=patient_with_teeth)
        assert history.count() == 1
        assert history.first().action == 'add_procedure'
        assert history.first().tooth_number == 1

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
        # First get available conditions
        conditions_url = reverse('dental-conditions', args=[clinic.id])
        conditions_response = authenticated_client.get(conditions_url)
        assert conditions_response.status_code == status.HTTP_200_OK
        
        # Use the first standard condition
        standard_condition = next(c for c in conditions_response.data['results'] if c['is_standard'])
        
        # Add the condition to a tooth
        url = reverse('add-tooth-condition', args=[clinic.id, patient_with_teeth.id, 1])
        data = {
            'condition_id': standard_condition['id'],
            'surface': 'occlusal',
            'notes': 'Using standard condition',
            'severity': 'moderate'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['condition_id'] == standard_condition['id']
        assert response.data['condition_name'] == standard_condition['name']
        assert response.data['surface'] == 'occlusal'
        assert response.data['notes'] == 'Using standard condition'

    def test_add_tooth_procedure_with_standard_procedure(self, authenticated_client, user, clinic, 
                                                       clinic_membership, patient_with_teeth,
                                                       standard_dental_procedures):
        """Test adding a standard procedure to a tooth."""
        # First get available procedures
        procedures_url = reverse('dental-procedures', args=[clinic.id])
        procedures_response = authenticated_client.get(procedures_url)
        assert procedures_response.status_code == status.HTTP_200_OK
        
        # Use the first standard procedure
        standard_procedure = next(p for p in procedures_response.data['results'] if p['is_standard'])
        
        # Add the procedure to a tooth
        url = reverse('add-tooth-procedure', args=[clinic.id, patient_with_teeth.id, 1])
        data = {
            'procedure_id': standard_procedure['id'],
            'surface': 'occlusal,buccal',
            'notes': 'Using standard procedure',
            'date_performed': '2023-12-01',
            'price': standard_procedure['default_price'],
            'status': 'completed'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['procedure_name'] == standard_procedure['name']
        assert response.data['surface'] == 'occlusal,buccal'
        assert response.data['notes'] == 'Using standard procedure'
        assert response.data['status'] == 'completed'
        assert float(response.data['price']) == float(standard_procedure['default_price'])

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