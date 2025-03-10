from django.contrib import admin
from .models import Patient, Appointment, Tooth, ToothCondition, Treatment, UserProfile

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'gender', 'phone', 'created_at')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('gender', 'created_at')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'dentist', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date', 'dentist')
    search_fields = ('patient__name', 'notes')
    date_hierarchy = 'date'

@admin.register(Tooth)
class ToothAdmin(admin.ModelAdmin):
    list_display = ('number', 'name')
    search_fields = ('number', 'name')
    ordering = ('number',)

@admin.register(ToothCondition)
class ToothConditionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'tooth', 'condition', 'appointment', 'status', 'cost')
    list_filter = ('status', 'condition', 'created_at')
    search_fields = ('patient__name', 'description')
    date_hierarchy = 'created_at'
