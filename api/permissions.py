from rest_framework import permissions
from api.models import ClinicMembership

class IsAdminOrDentist(permissions.BasePermission):
    """
    Custom permission to only allow admins or dentists to access the view.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has a profile with role admin or dentist
        try:
            return request.user.profile.role in ['admin', 'dentist']
        except:
            return False

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admins to access the view.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has a profile with role admin
        try:
            return request.user.profile.role == 'admin'
        except:
            return False

class IsClinicAdmin(permissions.BasePermission):
    """
    Custom permission to only allow clinic admins to access the view.
    Checks if the user is an admin of the clinic specified in the URL.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # For list views, allow any authenticated user
        if view.action == 'list':
            return True
        
        # For detail views, check if the user is an admin of the clinic
        try:
            # Get the clinic from the URL
            clinic_id = view.kwargs.get('pk') or view.kwargs.get('clinic_id')
            
            # Check if the user is an admin of this clinic
            return ClinicMembership.objects.filter(
                user=request.user,
                clinic_id=clinic_id,
                role='admin'
            ).exists()
        except:
            return False
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is an admin of the clinic associated with the object.
        """
        try:
            # Check if the object has a clinic attribute
            if hasattr(obj, 'clinic'):
                clinic = obj.clinic
            # If the object is a clinic itself
            else:
                clinic = obj
            
            # Check if the user is an admin of this clinic
            return ClinicMembership.objects.filter(
                user=request.user,
                clinic=clinic,
                role='admin'
            ).exists()
        except:
            return False

class IsClinicMember(permissions.BasePermission):
    """
    Custom permission to only allow members of a clinic to access its data.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get the clinic from the URL
        clinic_id = view.kwargs.get('pk') or view.kwargs.get('clinic_id')
        
        if not clinic_id:
            return True  # No clinic specified, let the view handle it
        
        # Check if the user is a member of this clinic
        return ClinicMembership.objects.filter(
            user=request.user,
            clinic_id=clinic_id
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user is a member of the clinic associated with the object.
        """
        try:
            # Check if the object has a clinic attribute
            if hasattr(obj, 'clinic'):
                clinic = obj.clinic
            # If the object is a clinic itself
            else:
                clinic = obj
            
            # Check if the user is a member of this clinic
            return ClinicMembership.objects.filter(
                user=request.user,
                clinic=clinic
            ).exists()
        except:
            return False

class HasClinicRole(permissions.BasePermission):
    """
    Custom permission to check if a user has a specific role in a clinic.
    """
    def __init__(self, roles):
        self.roles = roles if isinstance(roles, (list, tuple)) else [roles]
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Get the clinic from the URL
        clinic_id = view.kwargs.get('pk') or view.kwargs.get('clinic_id')
        
        if not clinic_id:
            return True  # No clinic specified, let the view handle it
        
        # Check if the user has the required role in this clinic
        return ClinicMembership.objects.filter(
            user=request.user,
            clinic_id=clinic_id,
            role__in=self.roles
        ).exists()
    
    def has_object_permission(self, request, view, obj):
        """
        Check if the user has the required role in the clinic associated with the object.
        """
        try:
            # Check if the object has a clinic attribute
            if hasattr(obj, 'clinic'):
                clinic = obj.clinic
            # If the object is a clinic itself
            else:
                clinic = obj
            
            # Check if the user has the required role in this clinic
            return ClinicMembership.objects.filter(
                user=request.user,
                clinic=clinic,
                role__in=self.roles
            ).exists()
        except:
            return False 