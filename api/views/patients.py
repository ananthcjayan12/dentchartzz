from rest_framework import filters
from api.models import Patient
from api.views.base import ClinicModelViewSet
from api.serializers.patients import PatientSerializer, PatientDetailSerializer

class PatientViewSet(ClinicModelViewSet):
    """
    ViewSet for managing patients within a clinic.
    
    This ViewSet provides CRUD operations for patients and ensures that
    users can only access patients from clinics they are members of.
    """
    queryset = Patient.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'phone', 'email']
    
    def get_serializer_class(self):
        """
        Return different serializers based on the action.
        
        For list actions, use the basic PatientSerializer.
        For retrieve, update, and create actions, use the detailed PatientDetailSerializer.
        """
        if self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update' or self.action == 'create':
            return PatientDetailSerializer
        return PatientSerializer 