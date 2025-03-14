from django.db import models
from api.models.clinics import Clinic

class Patient(models.Model):
    """
    Patient model for the API.
    Each patient belongs to a specific clinic.
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    # Clinic relationship - each patient belongs to a clinic
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='patients')
    
    # Personal Details
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Medical Information
    chief_complaint = models.TextField(blank=True, null=True)
    medical_history = models.TextField(blank=True, null=True)
    drug_allergies = models.TextField(blank=True, null=True)
    previous_dental_work = models.TextField(blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.clinic.name}"
    
    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['name']
        # Ensure uniqueness of patient within a clinic
        unique_together = [['name', 'phone', 'clinic']] 