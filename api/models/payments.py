from django.db import models
from django.contrib.auth.models import User
from datetime import date
from api.models.clinics import Clinic
from api.models.patients import Patient
from api.models.appointments import Appointment
from api.models.treatments import Treatment

class Payment(models.Model):
    """
    Payment model for the API.
    Each payment belongs to a specific clinic.
    """
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('insurance', 'Insurance'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]
    
    # Clinic relationship - each payment belongs to a clinic
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='payments')
    
    # Relationships
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='api_payments_created')
    
    # Payment details
    payment_date = models.DateField(default=date.today)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    notes = models.TextField(blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment #{self.id} - {self.patient.name} - {self.payment_date} - {self.clinic.name}"
    
    @property
    def balance(self):
        """Calculate the remaining balance for this payment"""
        return self.total_amount - self.amount_paid
    
    @property
    def is_balance_payment(self):
        """Check if this is a balance payment (amount_paid > 0 and total_amount = 0)"""
        return self.amount_paid > 0 and self.total_amount == 0
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date', '-created_at']

class PaymentItem(models.Model):
    """
    PaymentItem model for the API.
    Each payment item belongs to a specific payment and indirectly to a clinic.
    """
    # Relationships
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='items')
    treatment = models.ForeignKey(Treatment, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_items')
    
    # Item details
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.description} - ${self.amount} - {self.payment.clinic.name}"
    
    class Meta:
        verbose_name = 'Payment Item'
        verbose_name_plural = 'Payment Items'
        ordering = ['payment', 'id'] 