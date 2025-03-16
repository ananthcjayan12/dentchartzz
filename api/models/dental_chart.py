from django.db import models
from django.contrib.auth.models import User
from api.models import Patient, Clinic

class DentalCondition(models.Model):
    """Model for dental conditions like cavity, fracture, etc."""
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='dental_conditions')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, blank=True)  # Hex color code
    icon = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class DentalProcedure(models.Model):
    """Model for dental procedures like filling, extraction, etc."""
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='dental_procedures')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, blank=True)
    default_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_minutes = models.IntegerField(default=30)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class DentalChartTooth(models.Model):
    """Model for teeth in a dental chart."""
    QUADRANT_CHOICES = [
        ('upper_right', 'Upper Right'),
        ('upper_left', 'Upper Left'),
        ('lower_right', 'Lower Right'),
        ('lower_left', 'Lower Left'),
    ]
    
    TYPE_CHOICES = [
        ('incisor', 'Incisor'),
        ('canine', 'Canine'),
        ('premolar', 'Premolar'),
        ('molar', 'Molar'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='dental_chart_teeth')
    number = models.IntegerField()  # Standard tooth numbering (1-32 for adults)
    name = models.CharField(max_length=100)
    quadrant = models.CharField(max_length=20, choices=QUADRANT_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    class Meta:
        unique_together = ('patient', 'number')
    
    def __str__(self):
        return f"Tooth {self.number} ({self.name}) - {self.patient.name}"

class DentalChartCondition(models.Model):
    """Model for conditions applied to a specific tooth in the dental chart."""
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]
    
    tooth = models.ForeignKey(DentalChartTooth, on_delete=models.CASCADE, related_name='conditions')
    condition = models.ForeignKey(DentalCondition, on_delete=models.CASCADE)
    surface = models.CharField(max_length=50, blank=True)  # e.g., "occlusal,buccal"
    notes = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='moderate')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_dental_chart_conditions')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_dental_chart_conditions')
    
    def __str__(self):
        return f"{self.condition.name} on Tooth {self.tooth.number}"

class DentalChartProcedure(models.Model):
    """Model for procedures performed on a specific tooth in the dental chart."""
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    tooth = models.ForeignKey(DentalChartTooth, on_delete=models.CASCADE, related_name='procedures')
    procedure = models.ForeignKey(DentalProcedure, on_delete=models.CASCADE)
    surface = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    date_performed = models.DateTimeField(null=True, blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='performed_dental_chart_procedures')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.procedure.name} on Tooth {self.tooth.number}"

class ChartHistory(models.Model):
    """Model for tracking changes to a patient's dental chart."""
    ACTION_CHOICES = [
        ('add_condition', 'Add Condition'),
        ('update_condition', 'Update Condition'),
        ('remove_condition', 'Remove Condition'),
        ('add_procedure', 'Add Procedure'),
        ('update_procedure', 'Update Procedure'),
        ('cancel_procedure', 'Cancel Procedure'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='chart_history')
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    tooth_number = models.IntegerField()
    details = models.JSONField()  # Store action-specific details
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.action} on Tooth {self.tooth_number} by {self.user.get_full_name() or self.user.username}" 