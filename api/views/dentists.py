from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from api.views.base import ClinicViewSetMixin
from rest_framework.serializers import ModelSerializer
from api.models import ClinicMembership


class DentistSerializer(ModelSerializer):
    """
    Serializer for dentist users.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class DentistViewSet(ClinicViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing dentists within a clinic.
    
    This ViewSet provides read-only operations for dentists and ensures that
    users can only access dentists from clinics they are members of.
    """
    serializer_class = DentistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter users by clinic and role='dentist'.
        """
        # Skip filtering for Swagger documentation
        if getattr(self.request, 'swagger_fake_view', False):
            return User.objects.none()
            
        # Get the clinic from the URL
        clinic = self.get_clinic_from_url()
        
        # If clinic is None (for Swagger documentation), return an empty queryset
        if clinic is None:
            return User.objects.none()
        
        # Get users who are dentists in this clinic
        dentist_users = User.objects.filter(
            clinic_memberships__clinic=clinic,
            clinic_memberships__role='dentist'
        ).distinct()
        
        return dentist_users 