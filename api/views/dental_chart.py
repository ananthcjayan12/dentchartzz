from rest_framework import viewsets, status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime
from rest_framework.pagination import PageNumberPagination

from api.models.dental_chart import (
    DentalCondition, DentalProcedure, DentalChartTooth, 
    DentalChartCondition, DentalChartProcedure, ChartHistory
)
from api.models import Patient, Clinic
from api.serializers.dental_chart import (
    DentalConditionSerializer, DentalProcedureSerializer,
    DentalChartConditionSerializer, DentalChartProcedureSerializer,
    DentalChartSerializer, ChartHistorySerializer, DentalChartToothSerializer
)
from api.views.base import ClinicModelViewSet, ClinicViewSetMixin

class DentalConditionViewSet(ClinicModelViewSet):
    """ViewSet for dental conditions."""
    queryset = DentalCondition.objects.all()
    serializer_class = DentalConditionSerializer

class DentalProcedureViewSet(ClinicModelViewSet):
    """ViewSet for dental procedures."""
    queryset = DentalProcedure.objects.all()
    serializer_class = DentalProcedureSerializer

class DentalChartViewSet(ClinicViewSetMixin, GenericViewSet):
    """ViewSet for managing dental charts."""
    pagination_class = PageNumberPagination
    
    def retrieve(self, request, clinic_id=None, patient_id=None):
        """Get a patient's dental chart."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        
        # Ensure the patient has teeth records
        self._ensure_patient_has_teeth(patient)
        
        serializer = DentalChartSerializer(patient)
        return Response(serializer.data)
    
    def _ensure_patient_has_teeth(self, patient):
        """Create teeth records for the patient if they don't exist."""
        if not DentalChartTooth.objects.filter(patient=patient).exists():
            # Create standard adult dentition (32 teeth)
            teeth_data = [
                # Upper right quadrant (teeth 1-8)
                {'number': 1, 'name': 'Upper Right Third Molar', 'quadrant': 'upper_right', 'type': 'molar'},
                {'number': 2, 'name': 'Upper Right Second Molar', 'quadrant': 'upper_right', 'type': 'molar'},
                {'number': 3, 'name': 'Upper Right First Molar', 'quadrant': 'upper_right', 'type': 'molar'},
                {'number': 4, 'name': 'Upper Right Second Premolar', 'quadrant': 'upper_right', 'type': 'premolar'},
                {'number': 5, 'name': 'Upper Right First Premolar', 'quadrant': 'upper_right', 'type': 'premolar'},
                {'number': 6, 'name': 'Upper Right Canine', 'quadrant': 'upper_right', 'type': 'canine'},
                {'number': 7, 'name': 'Upper Right Lateral Incisor', 'quadrant': 'upper_right', 'type': 'incisor'},
                {'number': 8, 'name': 'Upper Right Central Incisor', 'quadrant': 'upper_right', 'type': 'incisor'},
                
                # Upper left quadrant (teeth 9-16)
                {'number': 9, 'name': 'Upper Left Central Incisor', 'quadrant': 'upper_left', 'type': 'incisor'},
                {'number': 10, 'name': 'Upper Left Lateral Incisor', 'quadrant': 'upper_left', 'type': 'incisor'},
                {'number': 11, 'name': 'Upper Left Canine', 'quadrant': 'upper_left', 'type': 'canine'},
                {'number': 12, 'name': 'Upper Left First Premolar', 'quadrant': 'upper_left', 'type': 'premolar'},
                {'number': 13, 'name': 'Upper Left Second Premolar', 'quadrant': 'upper_left', 'type': 'premolar'},
                {'number': 14, 'name': 'Upper Left First Molar', 'quadrant': 'upper_left', 'type': 'molar'},
                {'number': 15, 'name': 'Upper Left Second Molar', 'quadrant': 'upper_left', 'type': 'molar'},
                {'number': 16, 'name': 'Upper Left Third Molar', 'quadrant': 'upper_left', 'type': 'molar'},
                
                # Lower left quadrant (teeth 17-24)
                {'number': 17, 'name': 'Lower Left Third Molar', 'quadrant': 'lower_left', 'type': 'molar'},
                {'number': 18, 'name': 'Lower Left Second Molar', 'quadrant': 'lower_left', 'type': 'molar'},
                {'number': 19, 'name': 'Lower Left First Molar', 'quadrant': 'lower_left', 'type': 'molar'},
                {'number': 20, 'name': 'Lower Left Second Premolar', 'quadrant': 'lower_left', 'type': 'premolar'},
                {'number': 21, 'name': 'Lower Left First Premolar', 'quadrant': 'lower_left', 'type': 'premolar'},
                {'number': 22, 'name': 'Lower Left Canine', 'quadrant': 'lower_left', 'type': 'canine'},
                {'number': 23, 'name': 'Lower Left Lateral Incisor', 'quadrant': 'lower_left', 'type': 'incisor'},
                {'number': 24, 'name': 'Lower Left Central Incisor', 'quadrant': 'lower_left', 'type': 'incisor'},
                
                # Lower right quadrant (teeth 25-32)
                {'number': 25, 'name': 'Lower Right Central Incisor', 'quadrant': 'lower_right', 'type': 'incisor'},
                {'number': 26, 'name': 'Lower Right Lateral Incisor', 'quadrant': 'lower_right', 'type': 'incisor'},
                {'number': 27, 'name': 'Lower Right Canine', 'quadrant': 'lower_right', 'type': 'canine'},
                {'number': 28, 'name': 'Lower Right First Premolar', 'quadrant': 'lower_right', 'type': 'premolar'},
                {'number': 29, 'name': 'Lower Right Second Premolar', 'quadrant': 'lower_right', 'type': 'premolar'},
                {'number': 30, 'name': 'Lower Right First Molar', 'quadrant': 'lower_right', 'type': 'molar'},
                {'number': 31, 'name': 'Lower Right Second Molar', 'quadrant': 'lower_right', 'type': 'molar'},
                {'number': 32, 'name': 'Lower Right Third Molar', 'quadrant': 'lower_right', 'type': 'molar'},
            ]
            
            for tooth_data in teeth_data:
                DentalChartTooth.objects.create(patient=patient, **tooth_data)
    
    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, clinic_id=None, patient_id=None):
        """Get the history of changes to a patient's dental chart."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        
        history = ChartHistory.objects.filter(patient=patient)
        page = self.paginate_queryset(history)
        if page is not None:
            serializer = ChartHistorySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ChartHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='tooth/(?P<tooth_number>[0-9]+)/condition')
    def add_tooth_condition(self, request, clinic_id=None, patient_id=None, tooth_number=None):
        """Add a condition to a tooth."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        
        # Ensure the patient has teeth records
        self._ensure_patient_has_teeth(patient)
        
        tooth = get_object_or_404(DentalChartTooth, patient=patient, number=tooth_number)
        
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
        
        # Record in history
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='add_condition',
            tooth_number=tooth_number,
            details={
                'condition_name': condition.name,
                'surface': tooth_condition.surface
            }
        )
        
        serializer = DentalChartConditionSerializer(tooth_condition)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'], url_path='tooth/(?P<tooth_number>[0-9]+)/condition/(?P<condition_id>[0-9]+)')
    def update_tooth_condition(self, request, clinic_id=None, patient_id=None, tooth_number=None, condition_id=None):
        """Update a condition on a tooth."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        tooth = get_object_or_404(DentalChartTooth, patient=patient, number=tooth_number)
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
        
        # Record in history
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='update_condition',
            tooth_number=tooth_number,
            details={
                'condition_name': tooth_condition.condition.name,
                'surface': tooth_condition.surface
            }
        )
        
        serializer = DentalChartConditionSerializer(tooth_condition)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'], url_path='tooth/(?P<tooth_number>[0-9]+)/condition/(?P<condition_id>[0-9]+)')
    def delete_tooth_condition(self, request, clinic_id=None, patient_id=None, tooth_number=None, condition_id=None):
        """Delete a condition from a tooth."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        tooth = get_object_or_404(DentalChartTooth, patient=patient, number=tooth_number)
        tooth_condition = get_object_or_404(DentalChartCondition, id=condition_id, tooth=tooth)
        
        # Record in history before deleting
        condition_name = tooth_condition.condition.name
        surface = tooth_condition.surface
        
        tooth_condition.delete()
        
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='remove_condition',
            tooth_number=tooth_number,
            details={
                'condition_name': condition_name,
                'surface': surface
            }
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], url_path='tooth/(?P<tooth_number>[0-9]+)/procedure')
    def add_tooth_procedure(self, request, clinic_id=None, patient_id=None, tooth_number=None):
        """Add a procedure to a tooth."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        
        # Ensure the patient has teeth records
        self._ensure_patient_has_teeth(patient)
        
        tooth = get_object_or_404(DentalChartTooth, patient=patient, number=tooth_number)
        
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
        
        # Record in history
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='add_procedure',
            tooth_number=tooth_number,
            details={
                'procedure_name': procedure.name,
                'surface': tooth_procedure.surface,
                'status': tooth_procedure.status
            }
        )
        
        serializer = DentalChartProcedureSerializer(tooth_procedure)
        return Response(serializer.data, status=status.HTTP_201_CREATED) 