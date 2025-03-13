from django.contrib import admin
from .models import Patient, Appointment, Tooth, ToothCondition, Treatment, UserProfile, TreatmentHistory, Payment, PaymentItem

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

@admin.register(TreatmentHistory)
class TreatmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('treatment', 'previous_status', 'new_status', 'dentist', 'created_at')
    list_filter = ('new_status', 'created_at')
    search_fields = ('treatment__patient__name', 'notes')
    date_hierarchy = 'created_at'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'payment_date', 'total_amount', 'amount_paid', 'payment_method', 'created_by')
    list_filter = ('payment_method', 'payment_date', 'created_at')
    search_fields = ('patient__name', 'notes')
    date_hierarchy = 'payment_date'

@admin.register(PaymentItem)
class PaymentItemAdmin(admin.ModelAdmin):
    list_display = ('payment', 'description', 'amount', 'treatment')
    list_filter = ('payment__payment_date',)
    search_fields = ('description', 'payment__patient__name')
