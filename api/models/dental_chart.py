from django.db import models
from django.contrib.auth.models import User
from api.models import Patient, Clinic
from django.utils import timezone

class DentalCondition(models.Model):
    """Model for dental conditions like cavity, fracture, etc."""
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='dental_conditions')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    description = models.TextField(blank=True)
    color_code = models.CharField(max_length=7, blank=True)  # Hex color code
    icon = models.CharField(max_length=50, blank=True)
    is_standard = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
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
    is_standard = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    
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
    
    DENTITION_CHOICES = [
        ('permanent', 'Permanent'),
        ('primary', 'Primary'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='dental_chart_teeth')
    number = models.CharField(max_length=10)  # Changed to support A-T notation
    universal_number = models.IntegerField(null=True, blank=True)  # Made nullable for existing records
    dentition_type = models.CharField(
        max_length=10,
        choices=DENTITION_CHOICES,
        default='permanent'
    )
    name = models.CharField(max_length=100)
    quadrant = models.CharField(max_length=20, choices=QUADRANT_CHOICES)
    
    class Meta:
        unique_together = ('patient', 'number', 'dentition_type')
    
    def __str__(self):
        return f"Tooth {self.number} ({self.name}) - {self.patient.name} ({self.get_dentition_type_display()})"

class DentalChartCondition(models.Model):
    """Model for conditions on a specific tooth in the dental chart."""
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]
    
    tooth = models.ForeignKey(DentalChartTooth, on_delete=models.CASCADE, related_name='conditions')
    condition = models.ForeignKey(DentalCondition, on_delete=models.CASCADE)
    surface = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
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
    description = models.TextField(blank=True)
    date_performed = models.DateTimeField(null=True, blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='performed_dental_chart_procedures')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.procedure.name} on Tooth {self.tooth.number}"

class ProcedureNote(models.Model):
    """Model for procedure progress notes."""
    procedure = models.ForeignKey('DentalChartProcedure', on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    appointment_date = models.DateTimeField()
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-appointment_date']

class ChartHistory(models.Model):
    ACTIONS = [
        ('add_condition', 'Add Condition'),
        ('update_condition', 'Update Condition'),
        ('remove_condition', 'Remove Condition'),
        ('add_procedure', 'Add Procedure'),
        ('update_procedure', 'Update Procedure'),
        ('remove_procedure', 'Remove Procedure'),
        ('add_procedure_note', 'Add Procedure Note'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50, choices=ACTIONS)
    tooth_number = models.CharField(max_length=10)
    category = models.CharField(max_length=50, null=True, blank=True)
    details = models.JSONField()

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['patient', 'tooth_number']),
            models.Index(fields=['patient', 'category']),
            models.Index(fields=['patient', 'date'])
        ]

    def __str__(self):
        return f"{self.action} on Tooth {self.tooth_number} by {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Ensure that the tooth_number is always stored as a string
        self.tooth_number = str(self.tooth_number)
        super().save(*args, **kwargs) 