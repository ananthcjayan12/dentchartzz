from django.db import models
from django.contrib.auth.models import User
from api.models.clinics import Clinic
from api.models.patients import Patient
from api.models.appointments import Appointment
from api.models.teeth import Tooth, ToothCondition

class Treatment(models.Model):
    """
    Treatment model for the API.
    Each treatment belongs to a specific clinic.
    """
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Clinic relationship - each treatment belongs to a clinic
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='treatments')
    
    # Relationships
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatments')
    tooth = models.ForeignKey(Tooth, on_delete=models.CASCADE, related_name='treatments', null=True, blank=True)
    condition = models.ForeignKey(ToothCondition, on_delete=models.CASCADE, related_name='treatments')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='treatments', null=True, blank=True)
    
    # Treatment details
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        tooth_info = f" - Tooth {self.tooth.number}" if self.tooth else ""
        return f"{self.patient.name}{tooth_info} - {self.condition.name} - {self.clinic.name}"
    
    class Meta:
        verbose_name = 'Treatment'
        verbose_name_plural = 'Treatments'
        ordering = ['-created_at']

class TreatmentHistory(models.Model):
    """
    TreatmentHistory model for the API.
    Tracks treatment status changes over time.
    Each treatment history entry belongs to a specific clinic.
    """
    # Clinic relationship - each treatment history belongs to a clinic
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='treatment_histories')
    
    # Relationships
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name='history')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='treatment_history')
    dentist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='api_treatment_history')
    
    # History details
    previous_status = models.CharField(max_length=20, choices=Treatment.STATUS_CHOICES, null=True, blank=True)
    new_status = models.CharField(max_length=20, choices=Treatment.STATUS_CHOICES)
    notes = models.TextField(blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        previous = self.get_previous_status_display() if self.previous_status else "None"
        return f"{self.treatment} - Status changed from {previous} to {self.get_new_status_display()} - {self.clinic.name}"
    
    class Meta:
        verbose_name = 'Treatment History'
        verbose_name_plural = 'Treatment Histories'
        ordering = ['-created_at'] 