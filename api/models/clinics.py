from django.db import models
from django.contrib.auth.models import User

class Clinic(models.Model):
    """
    Clinic model representing a dental clinic.
    This is the top-level entity in the multi-clinic architecture.
    """
    SUBSCRIPTION_PLANS = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    SUBSCRIPTION_STATUS = [
        ('active', 'Active'),
        ('trial', 'Trial'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_PLANS, default='basic')
    subscription_status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='active')
    settings = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Clinic'
        verbose_name_plural = 'Clinics'
        ordering = ['name']


class ClinicMembership(models.Model):
    """
    ClinicMembership model representing the relationship between a user and a clinic.
    This allows users to be members of multiple clinics with different roles.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('dentist', 'Dentist'),
        ('staff', 'Staff'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clinic_memberships')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'clinic')
        verbose_name = 'Clinic Membership'
        verbose_name_plural = 'Clinic Memberships'
        ordering = ['clinic', 'user']
        
    def __str__(self):
        return f"{self.user.username} - {self.clinic.name} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        """
        Override save method to ensure only one primary clinic per user.
        """
        if self.is_primary:
            # Set all other memberships for this user to not primary
            ClinicMembership.objects.filter(
                user=self.user, 
                is_primary=True
            ).update(is_primary=False)
        
        super().save(*args, **kwargs) 