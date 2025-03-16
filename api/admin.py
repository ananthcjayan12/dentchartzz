from django.contrib import admin
from api.models.clinics import Clinic, ClinicMembership
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

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

# Register the ClinicMembership model
@admin.register(ClinicMembership)
class ClinicMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'clinic', 'role', 'is_primary')
    list_filter = ('role', 'is_primary', 'clinic')
    search_fields = ('user__username', 'user__email', 'clinic__name')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
