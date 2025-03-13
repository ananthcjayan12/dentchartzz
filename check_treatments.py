import os
import django
import sys
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

try:
    # Import models
    from app.models import Patient, Treatment, Payment
    from django.db.models import Sum
    
    # Get the patient (assuming patient ID 1 from the screenshot)
    patient_id = 1
    patient = Patient.objects.get(id=patient_id)
    print(f"Patient: {patient.name}")
    
    # Get treatments
    treatments = Treatment.objects.filter(patient=patient)
    print(f"\nTreatments: {treatments.count()}")
    total_treatment_cost = treatments.aggregate(Sum('cost'))['cost__sum'] or 0
    print(f"Total treatment cost: ${total_treatment_cost}")
    
    for treatment in treatments:
        print(f"- {treatment.condition.name}: ${treatment.cost} ({treatment.status})")
    
    # Get payments
    payments = Payment.objects.filter(patient=patient)
    print(f"\nPayments: {payments.count()}")
    total_amount = payments.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_paid = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    print(f"Total amount billed: ${total_amount}")
    print(f"Total amount paid: ${total_paid}")
    
    for payment in payments:
        print(f"- Payment #{payment.id}: total=${payment.total_amount}, paid=${payment.amount_paid}, balance=${payment.balance}")
        
    # Calculate balance
    balance_due = total_treatment_cost - total_paid
    print(f"\nBalance due (treatment cost - amount paid): ${balance_due}")
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1) 