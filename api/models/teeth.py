from django.db import models
from api.models.clinics import Clinic

class Tooth(models.Model):
    """
    Tooth model for the API.
    Teeth are global and not clinic-specific, as dental notation is standardized.
    """
    # Using double-digit tooth numbering system
    # First digit is the quadrant (1-4), second digit is the tooth position (1-8)
    number = models.IntegerField()
    name = models.CharField(max_length=50)
    quadrant = models.IntegerField(choices=[
        (1, 'Upper Right'), 
        (2, 'Upper Left'), 
        (3, 'Lower Left'), 
        (4, 'Lower Right')
    ], null=True, blank=True)
    position = models.IntegerField(help_text="Position within the quadrant (1-8)", null=True, blank=True)
    
    def __str__(self):
        return f"Tooth {self.number} - {self.name}"
    
    class Meta:
        verbose_name = 'Tooth'
        verbose_name_plural = 'Teeth'
        ordering = ['number']

class ToothCondition(models.Model):
    """
    ToothCondition model for the API.
    Each clinic can have its own set of tooth conditions.
    """
    # Clinic relationship - each tooth condition belongs to a clinic
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='tooth_conditions')
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} - {self.clinic.name}"
    
    class Meta:
        verbose_name = 'Tooth Condition'
        verbose_name_plural = 'Tooth Conditions'
        ordering = ['name']
        # Ensure uniqueness of condition name within a clinic
        unique_together = [['name', 'clinic']] 