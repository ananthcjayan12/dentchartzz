from django.urls import path
from . import views
from .health import health_check

urlpatterns = [
    # Health check endpoint
    path('health/', health_check, name='health_check'),
    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Patient URLs
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.patient_create, name='patient_create'),
    path('patients/create-ajax/', views.patient_create_ajax, name='patient_create_ajax'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_update, name='patient_update'),
    
    # Appointment URLs
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/calendar/', views.appointment_calendar, name='appointment_calendar'),
    path('appointments/add/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.appointment_update, name='appointment_update'),
    path('appointments/<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    path('appointments/<int:pk>/status/', views.appointment_status_update, name='appointment_status_update'),
    
    # Dental Chart and Treatment URLs
    path('patients/<int:patient_id>/dental-chart/', views.dental_chart, name='dental_chart'),
    path('patients/<int:patient_id>/add-treatment/', views.add_treatment, name='add_treatment'),
    path('treatments/tooth/<int:tooth_id>/', views.get_tooth_treatments, name='get_tooth_treatments'),
    path('treatments/<int:pk>/', views.treatment_detail, name='treatment_detail'),
    path('treatments/<int:pk>/update/', views.treatment_update, name='treatment_update'),
    
    # Payment URLs
    path('patients/<int:patient_id>/payments/', views.payment_list, name='payment_list'),
    path('patients/<int:patient_id>/payments/create/', views.payment_create, name='payment_create'),
    path('patients/<int:patient_id>/payments/balance/', views.payment_balance, name='payment_balance'),
    path('patients/<int:patient_id>/appointments/<int:appointment_id>/payments/create/', views.payment_create, name='payment_create_from_appointment'),
    path('payments/<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('api/patients/<int:patient_id>/balance/', views.get_patient_balance, name='get_patient_balance'),
    
    # API Endpoints
    path('api/patient/<int:patient_id>/complaints/', views.get_patient_complaints, name='get_patient_complaints'),
    path('api/time-slots/', views.get_time_slots, name='get_time_slots'),
] 