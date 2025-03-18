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
from api.views import dentists
from api.views import dental_chart

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
clinic_router.register(r'dentists', dentists.DentistViewSet, basename='clinic-dentist')

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
    path('clinics/<int:clinic_id>/time-slots/', 
         appointments.AppointmentViewSet.as_view({'get': 'time_slots'}), 
         name='time_slots'),
    
    # Dental Chart endpoints
    path('clinics/<int:clinic_id>/dental-conditions/', 
         dental_chart.DentalConditionViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='dental-conditions'),
    path('clinics/<int:clinic_id>/dental-procedures/', 
         dental_chart.DentalProcedureViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='dental-procedures'),
    path('clinics/<int:clinic_id>/patients/<int:patient_id>/dental-chart/', 
         dental_chart.DentalChartViewSet.as_view({'get': 'retrieve'}), 
         name='dental-chart'),
    path('clinics/<int:clinic_id>/patients/<int:patient_id>/dental-chart/history/', 
         dental_chart.DentalChartViewSet.as_view({'get': 'history'}), 
         name='dental-chart-history'),
    path('clinics/<int:clinic_id>/patients/<int:patient_id>/dental-chart/tooth/<str:tooth_number>/condition/', 
         dental_chart.DentalChartViewSet.as_view({'post': 'add_tooth_condition'}), 
         name='add-tooth-condition'),
    path('clinics/<int:clinic_id>/patients/<int:patient_id>/dental-chart/tooth/<str:tooth_number>/procedure/', 
         dental_chart.DentalChartViewSet.as_view({'post': 'add_tooth_procedure'}), 
         name='add-tooth-procedure'),
    path('clinics/<int:clinic_id>/patients/<int:patient_id>/dental-chart/tooth/<int:tooth_number>/condition/<int:condition_id>/', 
         dental_chart.DentalChartViewSet.as_view({
             'patch': 'update_tooth_condition',
             'delete': 'delete_tooth_condition'
         }), 
         name='tooth-condition-detail'),
] 