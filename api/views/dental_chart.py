from rest_framework import viewsets, status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime
from rest_framework.pagination import PageNumberPagination
from django.db import models

from api.models.dental_chart import (
    DentalCondition, DentalProcedure, DentalChartTooth, 
    DentalChartCondition, DentalChartProcedure, ChartHistory
)
from api.models import Patient, Clinic
from api.serializers.dental_chart import (
    DentalConditionSerializer, DentalProcedureSerializer,
    DentalChartConditionSerializer, DentalChartProcedureSerializer,
    DentalChartSerializer, ChartHistorySerializer, DentalChartToothSerializer,
    DentalChartViewSerializer
)
from api.views.base import ClinicModelViewSet, ClinicViewSetMixin

class DentalConditionViewSet(ClinicModelViewSet):
    """ViewSet for dental conditions."""
    queryset = DentalCondition.objects.all()
    serializer_class = DentalConditionSerializer
    
    def get_queryset(self):
        """Filter conditions by clinic and search parameters."""
        queryset = super().get_queryset()
        
        # Apply search filter if provided
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) | 
                models.Q(description__icontains=search) |
                models.Q(code__icontains=search)
            )
        
        return queryset.order_by('name')
    
    def create(self, request, *args, **kwargs):
        """Create a custom dental condition."""
        clinic = self.get_clinic_from_url()
        
        # Add clinic to request data
        data = request.data.copy()
        data['clinic'] = clinic.id
        
        # Set is_standard to False for custom conditions
        data['is_standard'] = False
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class DentalProcedureViewSet(ClinicModelViewSet):
    """ViewSet for dental procedures."""
    queryset = DentalProcedure.objects.all()
    serializer_class = DentalProcedureSerializer
    
    def get_queryset(self):
        """Filter procedures by clinic and category."""
        queryset = super().get_queryset()
        
        # Apply category filter if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Apply search filter if provided
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search) | 
                models.Q(description__icontains=search) |
                models.Q(code__icontains=search)
            )
        
        return queryset.order_by('name')
    
    def create(self, request, *args, **kwargs):
        """Create a custom dental procedure."""
        clinic = self.get_clinic_from_url()
        
        # Add clinic to request data
        data = request.data.copy()
        data['clinic'] = clinic.id
        
        # Set is_standard to False for custom procedures
        data['is_standard'] = False
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class DentalChartViewSet(ClinicViewSetMixin, GenericViewSet):
    """ViewSet for managing dental charts."""
    pagination_class = PageNumberPagination
    serializer_class = DentalChartViewSerializer
    
    def retrieve(self, request, patient_id=None, **kwargs):
        """Get a patient's dental chart."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        
        # Get all teeth for this patient
        permanent_teeth = DentalChartTooth.objects.filter(
            patient=patient,
            dentition_type='permanent'
        ).order_by('number')
        
        primary_teeth = DentalChartTooth.objects.filter(
            patient=patient,
            dentition_type='primary'
        ).order_by('number')
        
        # Prepare response data
        data = {
            'id': patient.id,
            'patient_id': patient.id,
            'patient_name': patient.name,
            'last_updated': patient.updated_at,
            'permanent_teeth': DentalChartToothSerializer(permanent_teeth, many=True).data,
            'primary_teeth': DentalChartToothSerializer(primary_teeth, many=True).data
        }
        
        return Response(data)
    
    def _ensure_patient_has_teeth(self, patient):
        """Create teeth records for the patient if they don't exist."""
        if not DentalChartTooth.objects.filter(patient=patient).exists():
            # Create standard adult dentition (32 teeth)
            teeth_data = [
                # Upper right quadrant (teeth 1-8)
                {
                    'number': '1',
                    'universal_number': 1,
                    'name': 'Upper Right Third Molar',
                    'quadrant': 'upper_right',
                    'dentition_type': 'permanent'
                },
                {
                    'number': '2',
                    'universal_number': 2,
                    'name': 'Upper Right Second Molar',
                    'quadrant': 'upper_right',
                    'dentition_type': 'permanent'
                },
                {
                    'number': '3',
                    'universal_number': 3,
                    'name': 'Upper Right First Molar',
                    'quadrant': 'upper_right',
                    'dentition_type': 'permanent'
                },
                {
                    'number': '4',
                    'universal_number': 4,
                    'name': 'Upper Right Second Premolar',
                    'quadrant': 'upper_right',
                    'dentition_type': 'premolar'
                },
                {
                    'number': '5',
                    'universal_number': 5,
                    'name': 'Upper Right First Premolar',
                    'quadrant': 'upper_right',
                    'dentition_type': 'premolar'
                },
                {
                    'number': '6',
                    'universal_number': 6,
                    'name': 'Upper Right Canine',
                    'quadrant': 'upper_right',
                    'dentition_type': 'canine'
                },
                {
                    'number': '7',
                    'universal_number': 7,
                    'name': 'Upper Right Lateral Incisor',
                    'quadrant': 'upper_right',
                    'dentition_type': 'incisor'
                },
                {
                    'number': '8',
                    'universal_number': 8,
                    'name': 'Upper Right Central Incisor',
                    'quadrant': 'upper_right',
                    'dentition_type': 'incisor'
                },
                
                # Upper left quadrant (teeth 9-16)
                {
                    'number': '9',
                    'universal_number': 9,
                    'name': 'Upper Left Central Incisor',
                    'quadrant': 'upper_left',
                    'dentition_type': 'incisor'
                },
                {
                    'number': '10',
                    'universal_number': 10,
                    'name': 'Upper Left Lateral Incisor',
                    'quadrant': 'upper_left',
                    'dentition_type': 'incisor'
                },
                {
                    'number': '11',
                    'universal_number': 11,
                    'name': 'Upper Left Canine',
                    'quadrant': 'upper_left',
                    'dentition_type': 'canine'
                },
                {
                    'number': '12',
                    'universal_number': 12,
                    'name': 'Upper Left First Premolar',
                    'quadrant': 'upper_left',
                    'dentition_type': 'premolar'
                },
                {
                    'number': '13',
                    'universal_number': 13,
                    'name': 'Upper Left Second Premolar',
                    'quadrant': 'upper_left',
                    'dentition_type': 'premolar'
                },
                {
                    'number': '14',
                    'universal_number': 14,
                    'name': 'Upper Left First Molar',
                    'quadrant': 'upper_left',
                    'dentition_type': 'molar'
                },
                {
                    'number': '15',
                    'universal_number': 15,
                    'name': 'Upper Left Second Molar',
                    'quadrant': 'upper_left',
                    'dentition_type': 'molar'
                },
                {
                    'number': '16',
                    'universal_number': 16,
                    'name': 'Upper Left Third Molar',
                    'quadrant': 'upper_left',
                    'dentition_type': 'molar'
                },
                
                # Lower left quadrant (teeth 17-24)
                {
                    'number': '17',
                    'universal_number': 17,
                    'name': 'Lower Left Third Molar',
                    'quadrant': 'lower_left',
                    'dentition_type': 'molar'
                },
                {
                    'number': '18',
                    'universal_number': 18,
                    'name': 'Lower Left Second Molar',
                    'quadrant': 'lower_left',
                    'dentition_type': 'molar'
                },
                {
                    'number': '19',
                    'universal_number': 19,
                    'name': 'Lower Left First Molar',
                    'quadrant': 'lower_left',
                    'dentition_type': 'molar'
                },
                {
                    'number': '20',
                    'universal_number': 20,
                    'name': 'Lower Left Second Premolar',
                    'quadrant': 'lower_left',
                    'dentition_type': 'premolar'
                },
                {
                    'number': '21',
                    'universal_number': 21,
                    'name': 'Lower Left First Premolar',
                    'quadrant': 'lower_left',
                    'dentition_type': 'premolar'
                },
                {
                    'number': '22',
                    'universal_number': 22,
                    'name': 'Lower Left Canine',
                    'quadrant': 'lower_left',
                    'dentition_type': 'canine'
                },
                {
                    'number': '23',
                    'universal_number': 23,
                    'name': 'Lower Left Lateral Incisor',
                    'quadrant': 'lower_left',
                    'dentition_type': 'incisor'
                },
                {
                    'number': '24',
                    'universal_number': 24,
                    'name': 'Lower Left Central Incisor',
                    'quadrant': 'lower_left',
                    'dentition_type': 'incisor'
                },
                
                # Lower right quadrant (teeth 25-32)
                {
                    'number': '25',
                    'universal_number': 25,
                    'name': 'Lower Right Central Incisor',
                    'quadrant': 'lower_right',
                    'dentition_type': 'incisor'
                },
                {
                    'number': '26',
                    'universal_number': 26,
                    'name': 'Lower Right Lateral Incisor',
                    'quadrant': 'lower_right',
                    'dentition_type': 'incisor'
                },
                {
                    'number': '27',
                    'universal_number': 27,
                    'name': 'Lower Right Canine',
                    'quadrant': 'lower_right',
                    'dentition_type': 'canine'
                },
                {
                    'number': '28',
                    'universal_number': 28,
                    'name': 'Lower Right First Premolar',
                    'quadrant': 'lower_right',
                    'dentition_type': 'premolar'
                },
                {
                    'number': '29',
                    'universal_number': 29,
                    'name': 'Lower Right Second Premolar',
                    'quadrant': 'lower_right',
                    'dentition_type': 'premolar'
                },
                {
                    'number': '30',
                    'universal_number': 30,
                    'name': 'Lower Right First Molar',
                    'quadrant': 'lower_right',
                    'dentition_type': 'molar'
                },
                {
                    'number': '31',
                    'universal_number': 31,
                    'name': 'Lower Right Second Molar',
                    'quadrant': 'lower_right',
                    'dentition_type': 'molar'
                },
                {
                    'number': '32',
                    'universal_number': 32,
                    'name': 'Lower Right Third Molar',
                    'quadrant': 'lower_right',
                    'dentition_type': 'molar'
                },
            ]
            
            # Create teeth records
            for tooth_data in teeth_data:
                DentalChartTooth.objects.create(patient=patient, **tooth_data)
    
    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, clinic_id=None, patient_id=None):
        """Get the history of changes to a patient's dental chart."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        
        # Get chart history for this patient
        history = ChartHistory.objects.filter(patient=patient).order_by('-date')
        
        # Paginate results
        page = self.paginate_queryset(history)
        if page is not None:
            serializer = ChartHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ChartHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='tooth/(?P<tooth_number>[A-Za-z0-9]+)/condition')
    def add_tooth_condition(self, request, clinic_id=None, patient_id=None, tooth_number=None):
        """Add a condition to a tooth."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        
        # Ensure the patient has teeth records
        self._ensure_patient_has_teeth(patient)
        
        # Get the tooth
        tooth = get_object_or_404(DentalChartTooth, patient=patient, number=str(tooth_number))
        
        # Validate dentition type
        dentition_type = request.data.get('dentition_type')
        if dentition_type and dentition_type != tooth.dentition_type:
            return Response(
                {'error': f'Dentition type mismatch. Tooth {tooth_number} is {tooth.dentition_type}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if we're creating a custom condition or using an existing one
        if 'custom_name' in request.data:
            # Create a new custom condition
            custom_condition = DentalCondition.objects.create(
                clinic=clinic,
                name=request.data.get('custom_name'),
                code=request.data.get('custom_code', ''),
                description=request.data.get('custom_description', ''),
                color_code=request.data.get('custom_color_code', '#000000'),
                icon=request.data.get('custom_icon', ''),
                is_standard=False
            )
            condition = custom_condition
        else:
            # Validate the condition exists in this clinic
            condition_id = request.data.get('condition_id')
            condition = get_object_or_404(DentalCondition, id=condition_id, clinic=clinic)
        
        # Create the tooth condition
        tooth_condition = DentalChartCondition.objects.create(
            tooth=tooth,
            condition=condition,
            surface=request.data.get('surface', ''),
            notes=request.data.get('notes', ''),
            severity=request.data.get('severity', 'moderate'),
            created_by=request.user,
            updated_by=request.user
        )
        
        # Create history entry
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='add_condition',
            tooth_number=str(tooth_number),
            details={
                'condition_name': condition.name,
                'surface': tooth_condition.surface,
                'severity': tooth_condition.severity
            }
        )
        
        # Prepare response with additional fields
        response_data = DentalChartConditionSerializer(tooth_condition).data
        response_data['condition_name'] = condition.name
        response_data['condition_code'] = condition.code
        response_data['created_by'] = request.user.get_full_name() or request.user.username
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'], url_path='tooth/(?P<tooth_number>[A-Za-z0-9]+)/condition/(?P<condition_id>[0-9]+)')
    def update_tooth_condition(self, request, clinic_id=None, patient_id=None, tooth_number=None, condition_id=None):
        """Update a condition on a tooth."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        tooth = get_object_or_404(DentalChartTooth, patient=patient, number=str(tooth_number))
        tooth_condition = get_object_or_404(DentalChartCondition, id=condition_id, tooth=tooth)
        
        # Update the fields
        if 'surface' in request.data:
            tooth_condition.surface = request.data['surface']
        if 'notes' in request.data:
            tooth_condition.notes = request.data['notes']
        if 'severity' in request.data:
            tooth_condition.severity = request.data['severity']
        
        tooth_condition.updated_by = request.user
        tooth_condition.save()
        
        # Create history entry
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='update_condition',
            tooth_number=str(tooth_number),
            details={
                'condition_name': tooth_condition.condition.name,
                'surface': tooth_condition.surface,
                'severity': tooth_condition.severity
            }
        )
        
        serializer = DentalChartConditionSerializer(tooth_condition)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'], url_path='tooth/(?P<tooth_number>[A-Za-z0-9]+)/condition/(?P<condition_id>[0-9]+)')
    def delete_tooth_condition(self, request, clinic_id=None, patient_id=None, tooth_number=None, condition_id=None):
        """Delete a condition from a tooth."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        tooth = get_object_or_404(DentalChartTooth, patient=patient, number=str(tooth_number))
        tooth_condition = get_object_or_404(DentalChartCondition, id=condition_id, tooth=tooth)
        
        # Record in history before deleting
        condition_name = tooth_condition.condition.name
        surface = tooth_condition.surface
        
        tooth_condition.delete()
        
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='remove_condition',
            tooth_number=str(tooth_number),
            details={
                'condition_name': condition_name,
                'surface': surface
            }
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], url_path='tooth/(?P<tooth_number>[A-Za-z0-9]+)/procedure')
    def add_tooth_procedure(self, request, clinic_id=None, patient_id=None, tooth_number=None):
        """Add a procedure to a tooth."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        
        # Ensure the patient has teeth records
        self._ensure_patient_has_teeth(patient)
        
        # Get the tooth
        tooth = get_object_or_404(DentalChartTooth, patient=patient, number=str(tooth_number))
        
        # Check if we're creating a custom procedure or using an existing one
        if 'custom_name' in request.data:
            # Create a new custom procedure
            custom_procedure = DentalProcedure.objects.create(
                clinic=clinic,
                name=request.data.get('custom_name'),
                code=request.data.get('custom_code', ''),
                description=request.data.get('custom_description', ''),
                default_price=request.data.get('price', 0),
                duration_minutes=request.data.get('duration_minutes', 30),
                category=request.data.get('category', ''),
                is_standard=False
            )
            procedure = custom_procedure
        else:
            # Validate the procedure exists in this clinic
            procedure_id = request.data.get('procedure_id')
            procedure = get_object_or_404(DentalProcedure, id=procedure_id, clinic=clinic)
        
        # Parse date_performed if provided
        date_performed = None
        if 'date_performed' in request.data and request.data['date_performed']:
            try:
                date_performed = timezone.make_aware(
                    datetime.strptime(request.data['date_performed'], '%Y-%m-%d')
                )
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Create the tooth procedure
        tooth_procedure = DentalChartProcedure.objects.create(
            tooth=tooth,
            procedure=procedure,
            surface=request.data.get('surface', ''),
            notes=request.data.get('notes', ''),
            date_performed=date_performed,
            performed_by=request.user if date_performed else None,
            price=request.data.get('price', procedure.default_price),
            status=request.data.get('status', 'planned')
        )
        
        # Create history entry
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='add_procedure',
            tooth_number=str(tooth_number),
            details={
                'procedure_name': procedure.name,
                'surface': tooth_procedure.surface,
                'status': tooth_procedure.status,
                'price': str(tooth_procedure.price)
            }
        )
        
        # Prepare response with additional fields
        response_data = DentalChartProcedureSerializer(tooth_procedure).data
        response_data['procedure_name'] = procedure.name
        response_data['procedure_code'] = procedure.code
        response_data['performed_by'] = request.user.get_full_name() or request.user.username if date_performed else None
        
        return Response(response_data, status=status.HTTP_201_CREATED) 