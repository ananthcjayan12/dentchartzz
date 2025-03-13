import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

try:
    # Import models
    from app.models import Patient, Payment
    from django.db.models import Sum
    
    # Get the patient
    patient_id = 1
    patient = Patient.objects.get(id=patient_id)
    print(f"Patient: {patient.name}")
    
    # Get payments
    payments = Payment.objects.filter(patient=patient)
    print(f"\nPayments: {payments.count()}")
    
    # Calculate using the new method
    total_amount_billed = payments.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_paid = payments.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    balance_due = total_amount_billed - total_paid
    
    print(f"Total amount billed: ${total_amount_billed}")
    print(f"Total amount paid: ${total_paid}")
    print(f"Balance due: ${balance_due}")
    
    for payment in payments:
        print(f"- Payment #{payment.id}: total=${payment.total_amount}, paid=${payment.amount_paid}, balance=${payment.balance}")
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1) 