import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

try:
    # Import models
    from app.models import Patient, Treatment
    
    # Get the patient
    patient_id = 1
    patient = Patient.objects.get(id=patient_id)
    print(f"Patient: {patient.name}")
    
    # Get treatments
    treatments = Treatment.objects.filter(patient=patient)
    
    if treatments.count() == 0:
        print("No treatments found for this patient.")
        sys.exit(0)
    
    # Update treatment costs
    # Assuming we want to distribute the total payment amount ($1100) among the treatments
    total_to_distribute = 1100.00
    per_treatment = total_to_distribute / treatments.count()
    
    for treatment in treatments:
        treatment.cost = per_treatment
        treatment.save()
        print(f"Updated treatment {treatment.id} cost to ${per_treatment}")
    
    print(f"\nSuccessfully updated {treatments.count()} treatments with a total cost of ${total_to_distribute}")
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1) 