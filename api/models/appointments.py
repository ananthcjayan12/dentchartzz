from django.db import models
from django.contrib.auth.models import User
from api.models.clinics import Clinic
from api.models.patients import Patient

class Appointment(models.Model):
    """
    Appointment model for the API.
    Each appointment belongs to a specific clinic.
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    # Clinic relationship - each appointment belongs to a clinic
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='appointments')
    
    # Relationships
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    dentist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_dentist_appointments')
    
    # Appointment details
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.name} - {self.date} {self.start_time} - {self.clinic.name}"
    
    @property
    def duration(self):
        """Calculate the duration of the appointment in minutes."""
        if not self.start_time or not self.end_time:
            return 0
            
        from datetime import datetime, timedelta
        
        # Create datetime objects for start and end times (using today's date as it doesn't matter)
        today = datetime.today().date()
        start_datetime = datetime.combine(today, self.start_time)
        end_datetime = datetime.combine(today, self.end_time)
        
        # If end_time is earlier than start_time, it means the appointment ends the next day
        if end_datetime < start_datetime:
            end_datetime = end_datetime + timedelta(days=1)
            
        # Calculate the difference in minutes
        delta = end_datetime - start_datetime
        return int(delta.total_seconds() / 60)
    
    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-date', '-start_time'] 