from django.db import models
from django.contrib.auth.models import User
from api.models import Patient, Clinic
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

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

class ChartHistory(models.Model):
    """Model for tracking changes to dental charts."""
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
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
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

class ProcedureNote(models.Model):
    """Model for procedure progress notes."""
    procedure = models.ForeignKey('DentalChartProcedure', on_delete=models.CASCADE, related_name='notes')
    note = models.TextField()
    appointment_date = models.DateTimeField()
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-appointment_date']

class GeneralProcedure(models.Model):
    """Model for procedures that are not specific to any tooth."""
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='general_procedures')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='general_procedures')
    procedure = models.ForeignKey(DentalProcedure, on_delete=models.PROTECT, related_name='general_instances')
    dentist = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='performed_general_procedures')
    
    notes = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_performed = models.DateField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']  # Most recent first

    def __str__(self):
        return f"{self.procedure.name} for {self.patient.name} on {self.date_performed or 'Not performed'}"

@receiver(post_save, sender=Patient)
def create_dental_chart(sender, instance, created, **kwargs):
    """Create dental chart teeth when a patient is created."""
    if created:
        # Define permanent teeth data using FDI system
        permanent_teeth_data = [
            # Upper Right (1st quadrant)
            {'number': '11', 'name': 'Upper Right Central Incisor', 'quadrant': 'upper_right'},
            {'number': '12', 'name': 'Upper Right Lateral Incisor', 'quadrant': 'upper_right'},
            {'number': '13', 'name': 'Upper Right Canine', 'quadrant': 'upper_right'},
            {'number': '14', 'name': 'Upper Right First Premolar', 'quadrant': 'upper_right'},
            {'number': '15', 'name': 'Upper Right Second Premolar', 'quadrant': 'upper_right'},
            {'number': '16', 'name': 'Upper Right First Molar', 'quadrant': 'upper_right'},
            {'number': '17', 'name': 'Upper Right Second Molar', 'quadrant': 'upper_right'},
            {'number': '18', 'name': 'Upper Right Third Molar', 'quadrant': 'upper_right'},
            
            # Upper Left (2nd quadrant)
            {'number': '21', 'name': 'Upper Left Central Incisor', 'quadrant': 'upper_left'},
            {'number': '22', 'name': 'Upper Left Lateral Incisor', 'quadrant': 'upper_left'},
            {'number': '23', 'name': 'Upper Left Canine', 'quadrant': 'upper_left'},
            {'number': '24', 'name': 'Upper Left First Premolar', 'quadrant': 'upper_left'},
            {'number': '25', 'name': 'Upper Left Second Premolar', 'quadrant': 'upper_left'},
            {'number': '26', 'name': 'Upper Left First Molar', 'quadrant': 'upper_left'},
            {'number': '27', 'name': 'Upper Left Second Molar', 'quadrant': 'upper_left'},
            {'number': '28', 'name': 'Upper Left Third Molar', 'quadrant': 'upper_left'},
            
            # Lower Left (3rd quadrant)
            {'number': '31', 'name': 'Lower Left Central Incisor', 'quadrant': 'lower_left'},
            {'number': '32', 'name': 'Lower Left Lateral Incisor', 'quadrant': 'lower_left'},
            {'number': '33', 'name': 'Lower Left Canine', 'quadrant': 'lower_left'},
            {'number': '34', 'name': 'Lower Left First Premolar', 'quadrant': 'lower_left'},
            {'number': '35', 'name': 'Lower Left Second Premolar', 'quadrant': 'lower_left'},
            {'number': '36', 'name': 'Lower Left First Molar', 'quadrant': 'lower_left'},
            {'number': '37', 'name': 'Lower Left Second Molar', 'quadrant': 'lower_left'},
            {'number': '38', 'name': 'Lower Left Third Molar', 'quadrant': 'lower_left'},
            
            # Lower Right (4th quadrant)
            {'number': '41', 'name': 'Lower Right Central Incisor', 'quadrant': 'lower_right'},
            {'number': '42', 'name': 'Lower Right Lateral Incisor', 'quadrant': 'lower_right'},
            {'number': '43', 'name': 'Lower Right Canine', 'quadrant': 'lower_right'},
            {'number': '44', 'name': 'Lower Right First Premolar', 'quadrant': 'lower_right'},
            {'number': '45', 'name': 'Lower Right Second Premolar', 'quadrant': 'lower_right'},
            {'number': '46', 'name': 'Lower Right First Molar', 'quadrant': 'lower_right'},
            {'number': '47', 'name': 'Lower Right Second Molar', 'quadrant': 'lower_right'},
            {'number': '48', 'name': 'Lower Right Third Molar', 'quadrant': 'lower_right'},
        ]
        
        # Define primary teeth data
        primary_teeth_data = [
            # Upper Right
            {'number': 'A', 'name': 'Upper Right Primary Second Molar', 'quadrant': 'upper_right'},
            {'number': 'B', 'name': 'Upper Right Primary First Molar', 'quadrant': 'upper_right'},
            {'number': 'C', 'name': 'Upper Right Primary Canine', 'quadrant': 'upper_right'},
            {'number': 'D', 'name': 'Upper Right Primary Lateral Incisor', 'quadrant': 'upper_right'},
            {'number': 'E', 'name': 'Upper Right Primary Central Incisor', 'quadrant': 'upper_right'},
            
            # Upper Left
            {'number': 'F', 'name': 'Upper Left Primary Central Incisor', 'quadrant': 'upper_left'},
            {'number': 'G', 'name': 'Upper Left Primary Lateral Incisor', 'quadrant': 'upper_left'},
            {'number': 'H', 'name': 'Upper Left Primary Canine', 'quadrant': 'upper_left'},
            {'number': 'I', 'name': 'Upper Left Primary First Molar', 'quadrant': 'upper_left'},
            {'number': 'J', 'name': 'Upper Left Primary Second Molar', 'quadrant': 'upper_left'},
            
            # Lower Left
            {'number': 'K', 'name': 'Lower Left Primary Second Molar', 'quadrant': 'lower_left'},
            {'number': 'L', 'name': 'Lower Left Primary First Molar', 'quadrant': 'lower_left'},
            {'number': 'M', 'name': 'Lower Left Primary Canine', 'quadrant': 'lower_left'},
            {'number': 'N', 'name': 'Lower Left Primary Lateral Incisor', 'quadrant': 'lower_left'},
            {'number': 'O', 'name': 'Lower Left Primary Central Incisor', 'quadrant': 'lower_left'},
            
            # Lower Right
            {'number': 'P', 'name': 'Lower Right Primary Central Incisor', 'quadrant': 'lower_right'},
            {'number': 'Q', 'name': 'Lower Right Primary Lateral Incisor', 'quadrant': 'lower_right'},
            {'number': 'R', 'name': 'Lower Right Primary Canine', 'quadrant': 'lower_right'},
            {'number': 'S', 'name': 'Lower Right Primary First Molar', 'quadrant': 'lower_right'},
            {'number': 'T', 'name': 'Lower Right Primary Second Molar', 'quadrant': 'lower_right'},
        ]
        
        # Create permanent teeth records
        for tooth_data in permanent_teeth_data:
            DentalChartTooth.objects.create(
                patient=instance,
                dentition_type='permanent',
                **tooth_data
            )
        
        # Create primary teeth records
        for tooth_data in primary_teeth_data:
            DentalChartTooth.objects.create(
                patient=instance,
                dentition_type='primary',
                **tooth_data
            )