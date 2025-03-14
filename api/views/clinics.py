from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from api.models import Clinic, ClinicMembership
from api.serializers.clinics import (
    ClinicSerializer, 
    ClinicDetailSerializer, 
    ClinicMembershipSerializer,
    UserSerializer
)
from api.permissions import IsClinicAdmin
from drf_yasg.utils import swagger_auto_schema
from api.docs import CLINIC_LIST_DOCS, CLINIC_CREATE_DOCS

class ClinicViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing clinics.
    Users can only see and manage clinics they are members of.
    """
    serializer_class = ClinicSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only return clinics the user is a member of"""
        # Skip user check for Swagger documentation
        if getattr(self.request, 'swagger_fake_view', False):
            return Clinic.objects.none()
        return Clinic.objects.filter(memberships__user=self.request.user)
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'retrieve':
            return ClinicDetailSerializer
        return ClinicSerializer
    
    def get_permissions(self):
        """Only clinic admins can update or delete clinics"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsClinicAdmin()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        """When creating a clinic, add the current user as an admin"""
        clinic = serializer.save()
        # Add the current user as an admin of the clinic
        ClinicMembership.objects.create(
            user=self.request.user,
            clinic=clinic,
            role='admin',
            is_primary=True
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all members of a clinic"""
        clinic = self.get_object()
        memberships = ClinicMembership.objects.filter(clinic=clinic)
        serializer = ClinicMembershipSerializer(memberships, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to a clinic"""
        clinic = self.get_object()
        
        # Check if the user exists
        try:
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the user is already a member
        if ClinicMembership.objects.filter(user=user, clinic=clinic).exists():
            return Response(
                {'error': 'User is already a member of this clinic'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the membership
        role = request.data.get('role', 'staff')
        is_primary = request.data.get('is_primary', False)
        
        membership = ClinicMembership.objects.create(
            user=user,
            clinic=clinic,
            role=role,
            is_primary=is_primary
        )
        
        serializer = ClinicMembershipSerializer(membership)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        """Remove a member from a clinic"""
        clinic = self.get_object()
        
        # Check if the user exists
        try:
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the user is a member
        try:
            membership = ClinicMembership.objects.get(user=user, clinic=clinic)
        except ClinicMembership.DoesNotExist:
            return Response(
                {'error': 'User is not a member of this clinic'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Don't allow removing the last admin
        if membership.role == 'admin':
            admin_count = ClinicMembership.objects.filter(
                clinic=clinic, 
                role='admin'
            ).count()
            
            if admin_count <= 1:
                return Response(
                    {'error': 'Cannot remove the last admin of a clinic'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Delete the membership
        membership.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['patch'])
    def update_member(self, request, pk=None):
        """Update a member's role or primary status"""
        clinic = self.get_object()
        
        # Check if the user exists
        try:
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if the user is a member
        try:
            membership = ClinicMembership.objects.get(user=user, clinic=clinic)
        except ClinicMembership.DoesNotExist:
            return Response(
                {'error': 'User is not a member of this clinic'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update the membership
        if 'role' in request.data:
            # Don't allow changing the role of the last admin
            if membership.role == 'admin' and request.data['role'] != 'admin':
                admin_count = ClinicMembership.objects.filter(
                    clinic=clinic, 
                    role='admin'
                ).count()
                
                if admin_count <= 1:
                    return Response(
                        {'error': 'Cannot change the role of the last admin'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            membership.role = request.data['role']
        
        if 'is_primary' in request.data:
            membership.is_primary = request.data['is_primary']
        
        membership.save()
        
        serializer = ClinicMembershipSerializer(membership)
        return Response(serializer.data)

    @swagger_auto_schema(**CLINIC_LIST_DOCS)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    @swagger_auto_schema(**CLINIC_CREATE_DOCS)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
        
    @swagger_auto_schema(
        operation_description="""
        Get details of a specific clinic.
        
        This endpoint returns detailed information about a clinic, including its name, address, contact information, and settings.
        The authenticated user must be a member of the clinic to access this endpoint.
        """,
        responses={
            200: ClinicDetailSerializer,
            401: 'Authentication credentials were not provided',
            404: 'Clinic not found'
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs) 