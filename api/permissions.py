from rest_framework import permissions

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