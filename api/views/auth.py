from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from api.models import ClinicMembership
from api.serializers.auth import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ClinicSelectionSerializer,
    PasswordChangeSerializer
)
from drf_yasg.utils import swagger_auto_schema
from api.docs import LOGIN_DOCS, LOGOUT_DOCS, REGISTER_DOCS

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token view that returns user info and clinics along with tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    @swagger_auto_schema(**LOGIN_DOCS)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class RegisterView(CreateAPIView):
    """
    API view for user registration.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    
    @swagger_auto_schema(**REGISTER_DOCS)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class LogoutView(APIView):
    """
    API view for logging out a user by blacklisting their refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(**LOGOUT_DOCS)
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Token is invalid or expired'}, status=status.HTTP_400_BAD_REQUEST)

class UserInfoView(APIView):
    """
    API view for getting the current user's info.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="""
        Get the current user's information.
        
        This endpoint returns information about the authenticated user, including their username, email, and clinics they have access to.
        """,
        responses={
            200: UserSerializer,
            401: {
                'description': 'Authentication credentials were not provided',
                'example': {
                    'detail': 'Authentication credentials were not provided.'
                }
            }
        }
    )
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        
        # Get user's clinics
        memberships = ClinicMembership.objects.filter(user=user).select_related('clinic')
        clinics = []
        
        for membership in memberships:
            clinics.append({
                'id': membership.clinic.id,
                'name': membership.clinic.name,
                'role': membership.role,
                'is_primary': membership.is_primary,
            })
        
        # Get current clinic
        primary_membership = memberships.filter(is_primary=True).first()
        if primary_membership:
            current_clinic = {
                'id': primary_membership.clinic.id,
                'name': primary_membership.clinic.name,
                'role': primary_membership.role,
            }
        elif memberships.exists():
            first_membership = memberships.first()
            current_clinic = {
                'id': first_membership.clinic.id,
                'name': first_membership.clinic.name,
                'role': first_membership.role,
            }
        else:
            current_clinic = None
        
        return Response({
            'user': serializer.data,
            'clinics': clinics,
            'current_clinic': current_clinic
        })

class ClinicSelectionView(GenericAPIView):
    """
    API view for selecting a clinic.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClinicSelectionSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        clinic_id = serializer.validated_data['clinic_id']
        user = request.user
        
        # Get the membership
        try:
            membership = ClinicMembership.objects.get(user=user, clinic_id=clinic_id)
            
            # Set this clinic as primary
            membership.is_primary = True
            membership.save()
            
            return Response({
                'message': f"Successfully selected clinic: {membership.clinic.name}",
                'clinic': {
                    'id': membership.clinic.id,
                    'name': membership.clinic.name,
                    'role': membership.role,
                }
            })
        except ClinicMembership.DoesNotExist:
            return Response(
                {'detail': 'You are not a member of this clinic.'},
                status=status.HTTP_400_BAD_REQUEST
            )

class PasswordChangeView(GenericAPIView):
    """
    API view for changing password.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PasswordChangeSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK) 