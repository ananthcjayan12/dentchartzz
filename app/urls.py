from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Patient URLs
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/add/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_update, name='patient_update'),
    
    # Appointment URLs
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/calendar/', views.appointment_calendar, name='appointment_calendar'),
    path('appointments/add/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('appointments/<int:pk>/edit/', views.appointment_update, name='appointment_update'),
    path('appointments/<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),
    
    # Dental Chart and Treatment URLs
    path('patients/<int:patient_id>/dental-chart/', views.dental_chart, name='dental_chart'),
    path('patients/<int:patient_id>/add-treatment/', views.add_treatment, name='add_treatment'),
    path('treatments/tooth/<int:tooth_id>/', views.get_tooth_treatments, name='get_tooth_treatments'),
] 