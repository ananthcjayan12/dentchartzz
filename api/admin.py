from django.contrib import admin
from api.models.clinics import Clinic, ClinicMembership
from api.models.dental_chart import (
    DentalCondition, DentalProcedure, DentalChartTooth, 
    DentalChartCondition, DentalChartProcedure, ChartHistory,
    ProcedureNote, GeneralProcedure, GeneralProcedureNote
)
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from decimal import Decimal
from django.utils import timezone
from django.contrib import messages

# Define an inline admin descriptor for the ClinicMembership model
class ClinicMembershipInline(admin.TabularInline):
    model = ClinicMembership
    extra = 1
    verbose_name = "Clinic Membership"
    verbose_name_plural = "Clinic Memberships"

# Define a new User admin with the inline
class UserAdmin(BaseUserAdmin):
    inlines = (ClinicMembershipInline,)

# Register the Clinic model
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone_display', 'email_display', 'created_at')
    search_fields = ('name', 'address', 'phone', 'email')
    fieldsets = (
        (None, {'fields': ('name', 'address', 'phone', 'email')}),
        ('Subscription', {'fields': ('subscription_plan', 'subscription_status')}),
        ('Advanced', {'fields': ('settings',), 'classes': ('collapse',)}),
    )
    actions = ['backfill_dental_procedures', 'backfill_dental_conditions']
    
    def phone_display(self, obj):
        return obj.phone
    phone_display.short_description = 'Phone Number'
    
    def email_display(self, obj):
        return obj.email
    email_display.short_description = 'Email'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make settings field optional in the admin
        if 'settings' in form.base_fields:
            form.base_fields['settings'].required = False
        return form
    
    def save_model(self, request, obj, form, change):
        # Ensure settings is a dict if not provided
        if not obj.settings:
            obj.settings = {}
        super().save_model(request, obj, form, change)
    
    def backfill_dental_procedures(self, request, queryset):
        """Admin action to backfill standard dental procedures for selected clinics."""
        procedures = [
            {
                'name': "Scaling and Polishing",
                'code': "D1110",
                'description': "Full mouth scaling and polishing",
                'category': "general",
                'default_price': Decimal("150.00"),
                'duration_minutes': 60,
            },
            {
                'name': "Fluoride Treatment",
                'code': "F1234",
                'description': "Topical fluoride application",
                'category': "preventive",
                'default_price': Decimal("50.00"),
                'duration_minutes': 15,
            },
            {
                'name': "Oral Prophylaxis",
                'code': "O5678",
                'description': "Professional dental cleaning",
                'category': "general",
                'default_price': Decimal("120.00"),
                'duration_minutes': 45,
            },
            {
                'name': "Root Canal Treatment",
                'code': "D3310",
                'description': "Endodontic therapy on anterior tooth",
                'category': "endodontic",
                'default_price': Decimal("500.00"),
                'duration_minutes': 90,
            },
            {
                'name': "Composite Filling",
                'code': "D2330",
                'description': "Resin-based composite - one surface, anterior",
                'category': "restorative",
                'default_price': Decimal("150.00"),
                'duration_minutes': 45,
            },
            {
                'name': "Extraction - Simple",
                'code': "D7140",
                'description': "Extraction of erupted tooth or exposed root",
                'category': "oral_surgery",
                'default_price': Decimal("180.00"),
                'duration_minutes': 30,
            },
        ]
        
        total_created = 0
        for clinic in queryset:
            created_count = 0
            for proc in procedures:
                # Check if a procedure with the same code already exists for the clinic
                if not DentalProcedure.objects.filter(clinic=clinic, code=proc['code']).exists():
                    DentalProcedure.objects.create(
                        clinic=clinic,
                        name=proc['name'],
                        code=proc['code'],
                        description=proc['description'],
                        category=proc['category'],
                        default_price=proc['default_price'],
                        duration_minutes=proc['duration_minutes'],
                        created_at=timezone.now(),
                        is_standard=True,
                    )
                    created_count += 1
            
            total_created += created_count
            if created_count > 0:
                self.message_user(
                    request, 
                    f"Created {created_count} dental procedures for clinic '{clinic.name}'.",
                    messages.SUCCESS
                )
            else:
                self.message_user(
                    request, 
                    f"No new dental procedures needed for clinic '{clinic.name}'.",
                    messages.INFO
                )
        
        if total_created > 0:
            self.message_user(
                request, 
                f"Successfully created {total_created} dental procedures across {queryset.count()} clinics.",
                messages.SUCCESS
            )
        else:
            self.message_user(
                request, 
                "No new dental procedures were created. All procedures may already exist.",
                messages.INFO
            )
    
    backfill_dental_procedures.short_description = "Backfill standard dental procedures"
    
    def backfill_dental_conditions(self, request, queryset):
        """Admin action to backfill standard dental conditions for selected clinics."""
        conditions = [
            {
                'name': "Cavity",
                'code': "CAV",
                'description': "Dental caries or tooth decay",
                'color_code': "#FF0000",  # Red
                'icon': "cavity-icon",
            },
            {
                'name': "Missing Tooth",
                'code': "MT",
                'description': "Tooth is missing",
                'color_code': "#000000",  # Black
                'icon': "missing-icon",
            },
            {
                'name': "Filled",
                'code': "FIL",
                'description': "Tooth has been filled",
                'color_code': "#0000FF",  # Blue
                'icon': "filled-icon",
            },
            {
                'name': "Crown",
                'code': "CRN",
                'description': "Tooth has a crown",
                'color_code': "#FFD700",  # Gold
                'icon': "crown-icon",
            },
            {
                'name': "Root Canal",
                'code': "RCT",
                'description': "Root canal treated tooth",
                'color_code': "#800080",  # Purple
                'icon': "rct-icon",
            },
        ]
        
        total_created = 0
        for clinic in queryset:
            created_count = 0
            for cond in conditions:
                # Check if a condition with the same code already exists for the clinic
                if not DentalCondition.objects.filter(clinic=clinic, code=cond['code']).exists():
                    DentalCondition.objects.create(
                        clinic=clinic,
                        name=cond['name'],
                        code=cond['code'],
                        description=cond['description'],
                        color_code=cond['color_code'],
                        icon=cond['icon'],
                        created_at=timezone.now(),
                        is_standard=True,
                    )
                    created_count += 1
            
            total_created += created_count
            if created_count > 0:
                self.message_user(
                    request, 
                    f"Created {created_count} dental conditions for clinic '{clinic.name}'.",
                    messages.SUCCESS
                )
            else:
                self.message_user(
                    request, 
                    f"No new dental conditions needed for clinic '{clinic.name}'.",
                    messages.INFO
                )
        
        if total_created > 0:
            self.message_user(
                request, 
                f"Successfully created {total_created} dental conditions across {queryset.count()} clinics.",
                messages.SUCCESS
            )
        else:
            self.message_user(
                request, 
                "No new dental conditions were created. All conditions may already exist.",
                messages.INFO
            )
    
    backfill_dental_conditions.short_description = "Backfill standard dental conditions"

# Register the ClinicMembership model
@admin.register(ClinicMembership)
class ClinicMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'clinic', 'role', 'is_primary')
    list_filter = ('role', 'is_primary', 'clinic')
    search_fields = ('user__username', 'user__email', 'clinic__name')

# Register Dental Chart models
@admin.register(DentalProcedure)
class DentalProcedureAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'default_price', 'clinic', 'is_standard')
    list_filter = ('category', 'is_standard', 'clinic')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)

@admin.register(DentalCondition)
class DentalConditionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'color_code', 'clinic', 'is_standard')
    list_filter = ('is_standard', 'clinic')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)

@admin.register(GeneralProcedure)
class GeneralProcedureAdmin(admin.ModelAdmin):
    list_display = ('procedure', 'patient', 'status', 'date_performed', 'price', 'clinic')
    list_filter = ('status', 'clinic')
    search_fields = ('procedure__name', 'patient__name', 'procedure_notes')
    date_hierarchy = 'date_performed'
    raw_id_fields = ('patient', 'procedure', 'dentist')

@admin.register(DentalChartTooth)
class DentalChartToothAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'patient', 'dentition_type', 'quadrant')
    list_filter = ('dentition_type', 'quadrant')
    search_fields = ('number', 'name', 'patient__name')
    raw_id_fields = ('patient',)

@admin.register(ChartHistory)
class ChartHistoryAdmin(admin.ModelAdmin):
    list_display = ('patient', 'action', 'date', 'user', 'tooth_number', 'category')
    list_filter = ('action', 'category')
    search_fields = ('patient__name', 'tooth_number')
    date_hierarchy = 'date'
    raw_id_fields = ('patient', 'user')

# Optional: Register these if you need to manage them directly
@admin.register(DentalChartCondition)
class DentalChartConditionAdmin(admin.ModelAdmin):
    list_display = ('tooth', 'condition', 'severity', 'created_at')
    list_filter = ('severity',)
    search_fields = ('tooth__number', 'condition__name', 'description')
    raw_id_fields = ('tooth', 'condition', 'created_by', 'updated_by')

@admin.register(DentalChartProcedure)
class DentalChartProcedureAdmin(admin.ModelAdmin):
    list_display = ('tooth', 'procedure', 'status', 'date_performed', 'price')
    list_filter = ('status',)
    search_fields = ('tooth__number', 'procedure__name', 'description')
    date_hierarchy = 'date_performed'
    raw_id_fields = ('tooth', 'procedure', 'performed_by')

@admin.register(ProcedureNote)
class ProcedureNoteAdmin(admin.ModelAdmin):
    list_display = ('procedure', 'appointment_date', 'created_by', 'created_at')
    search_fields = ('note', 'procedure__procedure__name')
    date_hierarchy = 'appointment_date'
    raw_id_fields = ('procedure', 'created_by')

@admin.register(GeneralProcedureNote)
class GeneralProcedureNoteAdmin(admin.ModelAdmin):
    list_display = ('procedure', 'appointment_date', 'created_by', 'created_at')
    search_fields = ('note', 'procedure__procedure__name')
    date_hierarchy = 'appointment_date'
    raw_id_fields = ('procedure', 'created_by')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
