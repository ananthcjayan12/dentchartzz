from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('dentist', 'Dentist'),
        ('staff', 'Staff'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    # Personal Details
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField()
    
    # Medical Information
    chief_complaint = models.TextField()
    medical_history = models.TextField(blank=True, null=True)
    drug_allergies = models.TextField(blank=True, null=True)
    previous_dental_work = models.TextField(blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    dentist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dentist_appointments')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.name} - {self.date} {self.start_time}"
    
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
        ordering = ['-date', '-start_time']

class Tooth(models.Model):
    # Using double-digit tooth numbering system
    # First digit is the quadrant (1-4), second digit is the tooth position (1-8)
    number = models.IntegerField()
    name = models.CharField(max_length=50)
    quadrant = models.IntegerField(choices=[(1, 'Upper Right'), (2, 'Upper Left'), (3, 'Lower Left'), (4, 'Lower Right')], null=True, blank=True)
    position = models.IntegerField(help_text="Position within the quadrant (1-8)", null=True, blank=True)
    
    def __str__(self):
        return f"Tooth {self.number} - {self.name}"
    
    class Meta:
        ordering = ['number']

class ToothCondition(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class Treatment(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatments')
    tooth = models.ForeignKey(Tooth, on_delete=models.CASCADE, related_name='treatments', null=True, blank=True)
    condition = models.ForeignKey(ToothCondition, on_delete=models.CASCADE, related_name='treatments')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='treatments', null=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        tooth_info = f" - Tooth {self.tooth.number}" if self.tooth else ""
        return f"{self.patient.name}{tooth_info} - {self.condition.name}"

class TreatmentHistory(models.Model):
    """Model to track treatment status changes over time"""
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE, related_name='history')
    previous_status = models.CharField(max_length=20, choices=Treatment.STATUS_CHOICES, null=True, blank=True)
    new_status = models.CharField(max_length=20, choices=Treatment.STATUS_CHOICES)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='treatment_history')
    dentist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='treatment_history')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        previous = self.get_previous_status_display() if self.previous_status else "None"
        return f"{self.treatment} - Status changed from {previous} to {self.get_new_status_display()}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Treatment histories"
