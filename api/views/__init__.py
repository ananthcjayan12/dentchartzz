# Views package 

# Import views here for easy access
from api.views.base import ClinicModelViewSet, ClinicViewSetMixin
from api.views.clinics import ClinicViewSet
from api.views.patients import PatientViewSet
from api.views.appointments import AppointmentViewSet
from api.views.treatments import TreatmentViewSet, ToothViewSet
from api.views.payments import PaymentViewSet
from api.views.auth import (
    CustomTokenObtainPairView,
    RegisterView,
    LogoutView,
    UserInfoView,
    ClinicSelectionView,
    PasswordChangeView
)

# This allows importing directly from api.views
__all__ = [
    'ClinicModelViewSet',
    'ClinicViewSetMixin',
    'ClinicViewSet',
    'PatientViewSet',
    'AppointmentViewSet',
    'TreatmentViewSet',
    'ToothViewSet',
    'PaymentViewSet',
    'CustomTokenObtainPairView',
    'RegisterView',
    'LogoutView',
    'UserInfoView',
    'ClinicSelectionView',
    'PasswordChangeView',
] 