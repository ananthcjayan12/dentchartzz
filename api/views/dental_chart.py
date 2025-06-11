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
    DentalChartCondition, DentalChartProcedure, ChartHistory, ProcedureNote, GeneralProcedure, GeneralProcedureNote
)
from api.models import Patient, Clinic
from api.serializers.dental_chart import (
    DentalConditionSerializer, DentalProcedureSerializer,
    DentalChartConditionSerializer, DentalChartProcedureSerializer,
    DentalChartSerializer, ChartHistorySerializer, DentalChartToothSerializer,
    DentalChartViewSerializer, ProcedureNoteSerializer, GeneralProcedureSerializer, GeneralProcedureNoteSerializer
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
    
    @action(detail=True, methods=['get'], url_path='history')
    def get_chart_history(self, request, clinic_id=None, patient_id=None):
        """Get dental chart history with filtering options."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        
        # Filter parameters
        tooth_number = request.query_params.get('tooth_number')
        category = request.query_params.get('category')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        history = ChartHistory.objects.filter(patient=patient)
        
        if tooth_number:
            history = history.filter(tooth_number=tooth_number)
        if category:
            history = history.filter(category=category)
        if start_date:
            try:
                start = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
                history = history.filter(date__gte=start)
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if end_date:
            try:
                end = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
                history = history.filter(date__lte=end)
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
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
        
        tooth = get_object_or_404(
            DentalChartTooth,
            patient=patient,
            number=str(tooth_number)
        )
        
        # Check dentition type match if provided
        if 'dentition_type' in request.data:
            if request.data['dentition_type'] != tooth.dentition_type:
                return Response(
                    {
                        'error': f'Dentition type mismatch. Tooth {tooth_number} is {tooth.dentition_type}, '
                                f'but condition is for {request.data["dentition_type"]}'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Handle custom condition creation
        if 'custom_name' in request.data:
            condition = DentalCondition.objects.create(
                clinic=clinic,
                name=request.data['custom_name'],
                code=request.data['custom_code'],
                description=request.data.get('custom_description', ''),
                is_standard=False
            )
        else:
            condition = get_object_or_404(DentalCondition, id=request.data['condition_id'], clinic=clinic)
        
        # Create the tooth condition
        tooth_condition = DentalChartCondition.objects.create(
            tooth=tooth,
            condition=condition,
            surface=request.data.get('surface', ''),
            description=request.data.get('description', request.data.get('notes', '')),
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
            category='conditions',
            details={
                'condition_name': condition.name,
                'surface': tooth_condition.surface,
                'severity': tooth_condition.severity,
                'notes': tooth_condition.description
            }
        )
        
        # Prepare response with additional fields
        response_data = DentalChartConditionSerializer(tooth_condition).data
        
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
        if 'description' in request.data:
            tooth_condition.description = request.data['description']
        elif 'notes' in request.data:  # Handle 'notes' field as well
            tooth_condition.description = request.data['notes']
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
            category='conditions',
            details={
                'condition_name': tooth_condition.condition.name,
                'surface': tooth_condition.surface,
                'severity': tooth_condition.severity,
                'notes': tooth_condition.description  # Include notes in history
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
        severity = tooth_condition.severity
        notes = tooth_condition.description  # Capture notes before deletion
        
        tooth_condition.delete()
        
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='remove_condition',
            tooth_number=str(tooth_number),
            category='conditions',
            details={
                'condition_name': condition_name,
                'surface': surface,
                'severity': severity,
                'notes': notes  # Include notes in history
            }
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], url_path='tooth/(?P<tooth_number>[A-Za-z0-9]+)/procedure')
    def add_tooth_procedure(self, request, clinic_id=None, patient_id=None, tooth_number=None):
        """Add a procedure to a tooth."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
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
            description=request.data.get('description', ''),
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
            category='procedures',
            details={
                'procedure_name': procedure.name,
                'surface': tooth_procedure.surface,
                'status': tooth_procedure.status,
                'price': str(tooth_procedure.price)
            }
        )
        
        # Prepare response with additional fields
        response_data = DentalChartProcedureSerializer(tooth_procedure).data
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'], url_path='tooth/(?P<tooth_number>[A-Za-z0-9]+)/procedure/(?P<procedure_id>[0-9]+)')
    def update_tooth_procedure(self, request, clinic_id=None, patient_id=None, tooth_number=None, procedure_id=None):
        """Update a procedure on a tooth."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        tooth = get_object_or_404(DentalChartTooth, patient=patient, number=str(tooth_number))
        tooth_procedure = get_object_or_404(DentalChartProcedure, id=procedure_id, tooth=tooth)
        
        # Update the fields
        if 'surface' in request.data:
            tooth_procedure.surface = request.data['surface']
        if 'description' in request.data:
            tooth_procedure.description = request.data['description']
        if 'price' in request.data:
            tooth_procedure.price = request.data['price']
        if 'status' in request.data:
            tooth_procedure.status = request.data['status']
        if 'date_performed' in request.data:
            try:
                date_performed = timezone.make_aware(
                    datetime.strptime(request.data['date_performed'], '%Y-%m-%d')
                )
                tooth_procedure.date_performed = date_performed
                tooth_procedure.performed_by = request.user
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        tooth_procedure.save()
        
        # Create history entry
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='update_procedure',
            tooth_number=str(tooth_number),
            details={
                'procedure_name': tooth_procedure.procedure.name,
                'surface': tooth_procedure.surface,
                'status': tooth_procedure.status,
                'price': str(tooth_procedure.price)
            }
        )
        
        # Prepare response with additional fields
        response_data = DentalChartProcedureSerializer(tooth_procedure).data
        response_data['procedure_name'] = tooth_procedure.procedure.name
        response_data['procedure_code'] = tooth_procedure.procedure.code
        response_data['performed_by'] = tooth_procedure.performed_by.get_full_name() if tooth_procedure.performed_by else None
        
        return Response(response_data)
    
    @action(detail=True, methods=['delete'], url_path='tooth/(?P<tooth_number>[A-Za-z0-9]+)/procedure/(?P<procedure_id>[0-9]+)')
    def delete_tooth_procedure(self, request, clinic_id=None, patient_id=None, tooth_number=None, procedure_id=None):
        """Delete a procedure from a tooth."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        tooth = get_object_or_404(DentalChartTooth, patient=patient, number=str(tooth_number))
        tooth_procedure = get_object_or_404(DentalChartProcedure, id=procedure_id, tooth=tooth)
        
        # Record in history before deleting
        procedure_name = tooth_procedure.procedure.name
        surface = tooth_procedure.surface
        procedure_status = tooth_procedure.status
        price = tooth_procedure.price
        
        tooth_procedure.delete()
        
        # Create history entry
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='remove_procedure',
            tooth_number=str(tooth_number),
            details={
                'procedure_name': procedure_name,
                'surface': surface,
                'status': procedure_status,
                'price': str(price)
            }
        )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'], 
            url_path='tooth/(?P<tooth_number>[A-Za-z0-9]+)/procedure/(?P<procedure_id>[0-9]+)/notes')
    def add_procedure_note(self, request, clinic_id=None, patient_id=None, 
                          tooth_number=None, procedure_id=None):
        """Add a progress note to a procedure."""
        clinic = self.get_clinic_from_url()
        patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
        tooth = get_object_or_404(DentalChartTooth, patient=patient, number=str(tooth_number))
        procedure = get_object_or_404(DentalChartProcedure, id=procedure_id, tooth=tooth)
        
        try:
            appointment_date = timezone.make_aware(
                datetime.strptime(request.data['appointment_date'], '%Y-%m-%d %H:%M')
            )
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD HH:MM.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        note = ProcedureNote.objects.create(
            procedure=procedure,
            note=request.data['note'],
            appointment_date=appointment_date,
            created_by=request.user
        )
        
        # Create history entry
        ChartHistory.objects.create(
            patient=patient,
            user=request.user,
            action='add_procedure_note',
            tooth_number=str(tooth_number),
            category='procedures',
            details={
                'procedure_name': procedure.procedure.name,
                'note': note.note,
                'appointment_date': appointment_date.strftime('%Y-%m-%d %H:%M'),
                'status': procedure.status
            }
        )
        
        return Response(ProcedureNoteSerializer(note).data, 
                       status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    def add_general_procedure(self, request, clinic_id=None, patient_id=None):
        """Add a general procedure."""
        try:
            clinic = self.get_clinic_from_url()
            
            # First validate the input data
            serializer = GeneralProcedureSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'error': 'Invalid procedure data', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Then validate patient exists
            try:
                patient = Patient.objects.get(id=patient_id, clinic=clinic)
            except Patient.DoesNotExist:
                return Response(
                    {'error': 'Patient not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get the dental procedure
            try:
                procedure = DentalProcedure.objects.get(
                    id=request.data['procedure_id'],
                    clinic=clinic
                )
            except DentalProcedure.DoesNotExist:
                return Response(
                    {'error': 'Procedure not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create general procedure
            general_procedure = GeneralProcedure.objects.create(
                clinic=clinic,
                patient=patient,
                procedure=procedure,
                dentist=request.user,
                procedure_notes=request.data.get('procedure_notes'),
                description=request.data.get('description'),
                date_performed=request.data.get('date_performed'),
                price=request.data.get('price', procedure.default_price),
                status=request.data.get('status', 'planned')
            )
            
            # Create history entry
            ChartHistory.objects.create(
                patient=patient,
                user=request.user,
                action='add_general_procedure',
                category='procedures',
                details={
                    'procedure_name': procedure.name,
                    'status': general_procedure.status,
                    'price': str(general_procedure.price)
                }
            )
            
            return Response(
                GeneralProcedureSerializer(general_procedure).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['GET'])
    def list_general_procedures(self, request, clinic_id=None, patient_id=None):
        """List all general procedures for a patient."""
        try:
            clinic = self.get_clinic_from_url()
            patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
            
            procedures = GeneralProcedure.objects.filter(
                clinic=clinic,
                patient=patient
            ).order_by('-created_at')  # Explicitly order by creation time
            
            # Paginate results
            page = self.paginate_queryset(procedures)
            if page is not None:
                serializer = GeneralProcedureSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = GeneralProcedureSerializer(procedures, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['GET'], url_path='general-procedures/(?P<procedure_id>[0-9]+)')
    def get_general_procedure(self, request, clinic_id=None, patient_id=None, procedure_id=None):
        """Get a specific general procedure."""
        try:
            clinic = self.get_clinic_from_url()
            patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
            
            procedure = get_object_or_404(
                GeneralProcedure,
                id=procedure_id,
                clinic=clinic,
                patient=patient
            )
            
            serializer = GeneralProcedureSerializer(procedure)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['PATCH', 'PUT'], url_path='general-procedures/(?P<procedure_id>[0-9]+)')
    def update_general_procedure(self, request, clinic_id=None, patient_id=None, procedure_id=None):
        """Update a general procedure."""
        try:
            clinic = self.get_clinic_from_url()
            patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
            
            procedure = get_object_or_404(
                GeneralProcedure,
                id=procedure_id,
                clinic=clinic,
                patient=patient
            )
            
            # Update fields directly
            if 'procedure_notes' in request.data:  # Changed from notes
                procedure.procedure_notes = request.data['procedure_notes']
            if 'description' in request.data:
                procedure.description = request.data['description']
            if 'price' in request.data:
                procedure.price = request.data['price']
            if 'status' in request.data:
                procedure.status = request.data['status']
            if 'date_performed' in request.data:
                procedure.date_performed = request.data['date_performed']
            
            procedure.save()
            
            # Create history entry
            ChartHistory.objects.create(
                patient=patient,
                user=request.user,
                action='update_procedure',
                category='procedures',
                details={
                    'procedure_name': procedure.procedure.name,
                    'status': procedure.status,
                    'price': str(procedure.price)
                }
            )
            
            serializer = GeneralProcedureSerializer(procedure)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['DELETE'], url_path='general-procedures/(?P<procedure_id>[0-9]+)')
    def delete_general_procedure(self, request, clinic_id=None, patient_id=None, procedure_id=None):
        """Delete a general procedure."""
        try:
            clinic = self.get_clinic_from_url()
            patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
            
            procedure = get_object_or_404(
                GeneralProcedure,
                id=procedure_id,
                clinic=clinic,
                patient=patient
            )
            
            # Store procedure details before deletion for history
            procedure_name = procedure.procedure.name
            procedure_status = procedure.status
            procedure_price = procedure.price
            
            # Delete the procedure
            procedure.delete()
            
            # Create history entry
            ChartHistory.objects.create(
                patient=patient,
                user=request.user,
                action='remove_procedure',
                category='procedures',
                details={
                    'procedure_name': procedure_name,
                    'status': procedure_status,
                    'price': str(procedure_price),
                    'is_general': True
                }
            )
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'], 
            url_path='general-procedures/(?P<procedure_id>[0-9]+)/notes')
    def add_general_procedure_note(self, request, clinic_id=None, patient_id=None, procedure_id=None):
        """Add a progress note to a general procedure."""
        try:
            clinic = self.get_clinic_from_url()
            patient = get_object_or_404(Patient, id=patient_id, clinic=clinic)
            procedure = get_object_or_404(GeneralProcedure, 
                                        id=procedure_id, 
                                        clinic=clinic, 
                                        patient=patient)
            
            try:
                appointment_date = timezone.make_aware(
                    datetime.strptime(request.data['appointment_date'], '%Y-%m-%d %H:%M')
                )
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD HH:MM.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            note = GeneralProcedureNote.objects.create(
                procedure=procedure,
                note=request.data['note'],
                appointment_date=appointment_date,
                created_by=request.user
            )
            
            # Create history entry
            ChartHistory.objects.create(
                patient=patient,
                user=request.user,
                action='add_procedure_note',
                category='procedures',
                details={
                    'procedure_name': procedure.procedure.name,
                    'note': note.note,
                    'appointment_date': appointment_date.strftime('%Y-%m-%d %H:%M'),
                    'status': procedure.status,
                    'is_general': True
                }
            )
            
            return Response(
                GeneralProcedureNoteSerializer(note).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            ) 