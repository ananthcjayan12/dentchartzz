from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

# Import views
from api.views import clinics
from api.views import patients
from api.views import appointments
from api.views import treatments
from api.views import payments
from api.views import auth

router = DefaultRouter()
# Register viewsets
router.register(r'clinics', clinics.ClinicViewSet, basename='clinic')
# router.register(r'patients', patients.PatientViewSet)
# router.register(r'appointments', appointments.AppointmentViewSet)
# router.register(r'treatments', treatments.TreatmentViewSet)
# router.register(r'payments', payments.PaymentViewSet)

# Create nested routers for clinic-specific resources
clinic_router = DefaultRouter()
clinic_router.register(r'patients', patients.PatientViewSet, basename='clinic-patient')
clinic_router.register(r'appointments', appointments.AppointmentViewSet, basename='clinic-appointment')
clinic_router.register(r'treatments', treatments.TreatmentViewSet, basename='clinic-treatment')
clinic_router.register(r'teeth', treatments.ToothViewSet, basename='clinic-tooth')
clinic_router.register(r'payments', payments.PaymentViewSet, basename='clinic-payment')

urlpatterns = [
    path('', include(router.urls)),
    # Nested routes for clinic-specific resources
    path('clinics/<int:clinic_id>/', include(clinic_router.urls)),
    
    # Authentication endpoints
    path('auth/login/', auth.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', auth.RegisterView.as_view(), name='register'),
    path('auth/logout/', auth.LogoutView.as_view(), name='logout'),
    path('auth/user/', auth.UserInfoView.as_view(), name='user_info'),
    path('auth/select-clinic/', auth.ClinicSelectionView.as_view(), name='select_clinic'),
    path('auth/change-password/', auth.PasswordChangeView.as_view(), name='change_password'),
    
    # Time slots endpoint
    path('clinics/<int:clinic_id>/time-slots/', appointments.AppointmentViewSet.as_view({'get': 'time_slots'}), name='time_slots'),
] 