# Serializers package 

# Import serializers here for easy access
from api.serializers.patients import PatientSerializer, PatientDetailSerializer
from api.serializers.appointments import AppointmentSerializer, AppointmentDetailSerializer, UserSerializer
from api.serializers.treatments import (
    TreatmentSerializer, 
    TreatmentDetailSerializer, 
    ToothSerializer, 
    ToothConditionSerializer
)
from api.serializers.payments import PaymentSerializer, PaymentDetailSerializer, PaymentItemSerializer
from api.serializers.auth import (
    UserSerializer as AuthUserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    ClinicSelectionSerializer,
    PasswordChangeSerializer
)

# This allows importing directly from api.serializers
__all__ = [
    'PatientSerializer',
    'PatientDetailSerializer',
    'AppointmentSerializer',
    'AppointmentDetailSerializer',
    'UserSerializer',
    'TreatmentSerializer',
    'TreatmentDetailSerializer',
    'ToothSerializer',
    'ToothConditionSerializer',
    'PaymentSerializer',
    'PaymentDetailSerializer',
    'PaymentItemSerializer',
    'AuthUserSerializer',
    'RegisterSerializer',
    'CustomTokenObtainPairSerializer',
    'ClinicSelectionSerializer',
    'PasswordChangeSerializer',
] 