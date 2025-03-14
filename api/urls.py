from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import views here
# from api.views import patients, appointments, treatments, payments, auth

router = DefaultRouter()
# Register viewsets here
# router.register(r'patients', patients.PatientViewSet)
# router.register(r'appointments', appointments.AppointmentViewSet)
# router.register(r'treatments', treatments.TreatmentViewSet)
# router.register(r'payments', payments.PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Add other URL patterns here
    # path('auth/login/', auth.LoginView.as_view(), name='api_login'),
    # path('auth/logout/', auth.LogoutView.as_view(), name='api_logout'),
    # path('time-slots/', appointments.TimeSlotView.as_view(), name='time_slots'),
] 