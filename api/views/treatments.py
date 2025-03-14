from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from api.models import Treatment, TreatmentHistory, Tooth
from api.views.base import ClinicModelViewSet
from api.serializers.treatments import (
    TreatmentSerializer, 
    TreatmentDetailSerializer,
    ToothSerializer
)

class TreatmentViewSet(ClinicModelViewSet):
    """
    ViewSet for managing treatments within a clinic.
    
    This ViewSet provides CRUD operations for treatments and ensures that
    users can only access treatments from clinics they are members of.
    """
    queryset = Treatment.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['patient__name', 'description', 'condition__name']
    
    def get_queryset(self):
        """
        Filter treatments by clinic and optionally by patient, tooth, status, or appointment.
        """
        queryset = super().get_queryset()
        
        # Get query parameters
        patient_id = self.request.query_params.get('patient_id')
        tooth_id = self.request.query_params.get('tooth_id')
        status_param = self.request.query_params.get('status')
        appointment_id = self.request.query_params.get('appointment_id')
        
        # Filter by patient
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter by tooth
        if tooth_id:
            queryset = queryset.filter(tooth_id=tooth_id)
        
        # Filter by status
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by appointment
        if appointment_id:
            queryset = queryset.filter(appointment_id=appointment_id)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """
        Return different serializers based on the action.
        
        For list actions, use the basic TreatmentSerializer.
        For retrieve, update, and create actions, use the detailed TreatmentDetailSerializer.
        """
        if self.action in ['retrieve', 'update', 'partial_update', 'create']:
            return TreatmentDetailSerializer
        return TreatmentSerializer
    
    def get_serializer_context(self):
        """
        Add the clinic to the serializer context.
        """
        context = super().get_serializer_context()
        context['clinic'] = self.get_clinic_from_url()
        return context
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, clinic_id=None, pk=None):
        """
        Update the status of a treatment and create a treatment history entry.
        """
        treatment = self.get_object()
        
        # Get the new status from the request data
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')
        appointment_id = request.data.get('appointment_id')
        
        # Validate the new status
        if not new_status:
            return Response(
                {'detail': 'Status is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(Treatment.STATUS_CHOICES):
            return Response(
                {'detail': f'Invalid status. Must be one of: {", ".join(dict(Treatment.STATUS_CHOICES).keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the clinic
        clinic = self.get_clinic_from_url()
        
        # Create a treatment history entry
        TreatmentHistory.objects.create(
            clinic=clinic,
            treatment=treatment,
            previous_status=treatment.status,
            new_status=new_status,
            appointment_id=appointment_id,
            dentist=request.user,
            notes=notes
        )
        
        # Update the treatment status
        treatment.status = new_status
        treatment.save()
        
        # Return the updated treatment
        serializer = self.get_serializer(treatment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_tooth(self, request, clinic_id=None):
        """
        Get treatments for a specific tooth of a patient.
        """
        # Get query parameters
        patient_id = request.query_params.get('patient_id')
        tooth_id = request.query_params.get('tooth_id')
        
        # Validate parameters
        if not patient_id:
            return Response(
                {'detail': 'Patient ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not tooth_id:
            return Response(
                {'detail': 'Tooth ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the clinic
        clinic = self.get_clinic_from_url()
        
        # Get treatments for the tooth
        treatments = Treatment.objects.filter(
            clinic=clinic,
            patient_id=patient_id,
            tooth_id=tooth_id
        ).order_by('-created_at')
        
        # Serialize the treatments
        serializer = TreatmentSerializer(treatments, many=True)
        return Response(serializer.data)

class ToothViewSet(ClinicModelViewSet):
    """
    ViewSet for managing teeth.
    
    This ViewSet provides read-only operations for teeth.
    Teeth are global and not clinic-specific, as dental notation is standardized.
    """
    queryset = Tooth.objects.all()
    serializer_class = ToothSerializer
    
    def get_queryset(self):
        """
        Return all teeth, as they are global and not clinic-specific.
        """
        # Skip filtering for Swagger documentation
        if getattr(self.request, 'swagger_fake_view', False):
            return Tooth.objects.all().order_by('number')
            
        # Override the clinic filtering from ClinicModelViewSet
        return Tooth.objects.all().order_by('number')
    
    def get_clinic_from_url(self):
        """
        Override to handle the fact that teeth are global and not clinic-specific.
        """
        # Skip clinic check for Swagger documentation
        if getattr(self.request, 'swagger_fake_view', False):
            return None
            
        # For actions that need a clinic (like treatments), use the parent method
        if self.action in ['treatments']:
            return super().get_clinic_from_url()
            
        # For other actions, no clinic is needed
        return None
    
    @action(detail=True, methods=['get'])
    def treatments(self, request, clinic_id=None, pk=None):
        """
        Get treatments for a specific tooth across all patients in the clinic.
        """
        # Skip for Swagger documentation
        if getattr(self.request, 'swagger_fake_view', False):
            return Response([])
            
        # Get the tooth
        tooth = self.get_object()
        
        # Get the clinic
        clinic = self.get_clinic_from_url()
        
        # If clinic is None (for Swagger documentation), return empty list
        if clinic is None:
            return Response([])
        
        # Get treatments for the tooth in this clinic
        treatments = Treatment.objects.filter(
            clinic=clinic,
            tooth=tooth
        ).order_by('-created_at')
        
        # Serialize the treatments
        serializer = TreatmentSerializer(treatments, many=True)
        return Response(serializer.data) 