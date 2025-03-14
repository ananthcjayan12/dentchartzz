from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from api.models import Clinic, ClinicMembership

class ClinicViewSetMixin:
    """
    A mixin for ViewSets that filters queryset by clinic.
    
    This mixin should be used with all ViewSets that deal with clinic-specific data.
    It ensures that users can only access data from clinics they are members of.
    """
    
    def get_clinic_from_url(self):
        """
        Get the clinic from the URL.
        
        This method extracts the clinic_id from the URL and returns the Clinic object.
        If the clinic doesn't exist or the user is not a member, it raises PermissionDenied.
        """
        # Skip clinic check for Swagger documentation
        if getattr(self.request, 'swagger_fake_view', False):
            # Return None for Swagger
            return None
            
        # Get the clinic_id from the URL
        clinic_id = self.kwargs.get('clinic_id')
        
        if not clinic_id:
            # For Swagger documentation, don't raise an exception
            if getattr(self.request, 'swagger_fake_view', False):
                return None
            raise PermissionDenied("Clinic ID is required")
        
        # Check if the clinic exists and the user is a member
        try:
            clinic = Clinic.objects.get(id=clinic_id)
            
            # Check if the user is a member of this clinic
            is_member = ClinicMembership.objects.filter(
                user=self.request.user,
                clinic=clinic
            ).exists()
            
            if not is_member and not getattr(self.request, 'swagger_fake_view', False):
                raise PermissionDenied("You are not a member of this clinic")
                
            return clinic
        except Clinic.DoesNotExist:
            if getattr(self.request, 'swagger_fake_view', False):
                return None
            raise PermissionDenied("Clinic not found")
    
    def get_queryset(self):
        """
        Filter the queryset by clinic.
        
        This method ensures that users can only access data from clinics they are members of.
        """
        # Skip filtering for Swagger documentation
        if getattr(self.request, 'swagger_fake_view', False):
            return super().get_queryset().none()
            
        # Get the base queryset from the parent class
        queryset = super().get_queryset()
        
        # Get the clinic from the URL
        clinic = self.get_clinic_from_url()
        
        # If clinic is None (for Swagger documentation), return an empty queryset
        if clinic is None:
            return queryset.none()
        
        # Filter the queryset by clinic
        return queryset.filter(clinic=clinic)
    
    def perform_create(self, serializer):
        """
        Set the clinic when creating a new object.
        
        This method ensures that new objects are associated with the correct clinic.
        """
        # Skip for Swagger documentation
        if getattr(self.request, 'swagger_fake_view', False):
            return
            
        # Get the clinic from the URL
        clinic = self.get_clinic_from_url()
        
        # If clinic is None (for Swagger documentation), don't save
        if clinic is None:
            return
        
        # Save with the clinic
        serializer.save(clinic=clinic)

class ClinicModelViewSet(ClinicViewSetMixin, viewsets.ModelViewSet):
    """
    A ModelViewSet that filters queryset by clinic.
    
    This ViewSet should be used for all models that are clinic-specific.
    It ensures that users can only access data from clinics they are members of.
    """
    pass 