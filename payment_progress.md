# Payment System Implementation Plan

## Overview
This document outlines the implementation plan for a payment system in the dental practice management application. The payment system will be integrated into both the patient and appointment screens, allowing staff to track payments, manage outstanding balances, and record payment history.

## Requirements
1. Create a reusable payment card component that shows:
   - Total amount to be paid by patient
   - Due amount (outstanding balance)
   - Payment history

2. Add functionality to record new payments with:
   - Pre-filled patient information
   - Date of payment (defaulting to current date)
   - Ability to add multiple line items with individual costs
   - Total calculation
   - Amount paid field
   - Remaining balance calculation

## Implementation Plan

### Phase 1: Database Models (Estimated time: 2-3 hours)
1. Create `Payment` model:
   - Foreign key to Patient
   - Optional foreign key to Appointment
   - Payment date
   - Total amount
   - Amount paid
   - Payment method (cash, card, insurance, etc.)
   - Notes
   - Created by (staff member)
   - Created at timestamp

2. Create `PaymentItem` model:
   - Foreign key to Payment
   - Description
   - Amount
   - Related treatment (optional)

### Phase 2: Backend Implementation (Estimated time: 4-5 hours)
1. Create forms:
   - `PaymentForm` for the main payment details
   - `PaymentItemFormSet` for line items

2. Create views:
   - `payment_list` - List all payments for a patient
   - `payment_create` - Create a new payment
   - `payment_detail` - View payment details
   - `get_patient_balance` - API endpoint to calculate patient balance

3. Add URL patterns for the new views

4. Create utility functions:
   - Calculate total treatment cost for a patient
   - Calculate total payments made by a patient
   - Calculate outstanding balance

### Phase 3: Frontend Implementation (Estimated time: 5-6 hours)
1. Create templates:
   - `payment_card.html` - Reusable component for patient and appointment screens
   - `payment_form.html` - Form for adding new payments
   - `payment_detail.html` - Detailed view of a payment

2. Integrate payment card into:
   - Patient detail page
   - Appointment detail page

3. Implement JavaScript functionality:
   - Dynamic addition/removal of payment line items
   - Real-time calculation of totals
   - Form validation

### Phase 4: Testing and Refinement (Estimated time: 2-3 hours)
1. Test payment creation
2. Test payment history display
3. Test balance calculations
4. Fix any bugs or issues
5. Refine UI/UX based on feedback

## Detailed Model Design

### Payment Model
```python
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('insurance', 'Insurance'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='payments')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    payment_date = models.DateField(default=date.today)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment #{self.id} - {self.patient.name} - {self.payment_date}"
    
    @property
    def balance(self):
        return self.total_amount - self.amount_paid
    
    class Meta:
        ordering = ['-payment_date', '-created_at']
```

### PaymentItem Model
```python
class PaymentItem(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    treatment = models.ForeignKey(Treatment, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_items')
    
    def __str__(self):
        return f"{self.description} - ${self.amount}"
```

## UI Components

### Payment Card Component
The payment card will be a reusable component that shows:
- Total treatment cost
- Total amount paid
- Outstanding balance
- Recent payment history (last 3-5 payments)
- Button to add a new payment

### Payment Form
The payment form will include:
- Patient information (pre-filled, non-editable)
- Payment date (defaulting to current date)
- Payment method selection
- Dynamic line items section with:
  - Description field
  - Amount field
  - Option to add/remove line items
- Automatic calculation of total
- Amount paid field
- Calculated remaining balance
- Notes field
- Submit button

## Implementation Steps

1. Create the database models
2. Run migrations
3. Create forms and views
4. Create templates
5. Integrate with existing pages
6. Test and refine

## Next Steps After Approval
Once this plan is approved, we will proceed with the implementation starting with the database models and then moving on to the backend and frontend components. 