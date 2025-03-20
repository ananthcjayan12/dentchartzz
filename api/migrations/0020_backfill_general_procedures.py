from decimal import Decimal
from django.db import migrations
from django.utils import timezone

def create_general_procedures(apps, schema_editor):
    DentalProcedure = apps.get_model('api', 'DentalProcedure')
    Clinic = apps.get_model('api', 'Clinic')
    
    # Define the procedures to backfill
    procedures = [
        {
            'name': "Scaling and Polishing",
            'code': "D1110",
            'description': "Full mouth scaling and polishing",
            'category': "general",
            'default_price': Decimal("150.00"),
            'duration_minutes': 60,
        },
        {
            'name': "Fluoride Treatment",
            'code': "F1234",
            'description': "Topical fluoride application",
            'category': "preventive",
            'default_price': Decimal("50.00"),
            'duration_minutes': 15,
        },
        {
            'name': "Oral Prophylaxis",
            'code': "O5678",
            'description': "Professional dental cleaning",
            'category': "general",
            'default_price': Decimal("120.00"),
            'duration_minutes': 45,
        },
    ]
    
    clinics = Clinic.objects.all()
    for clinic in clinics:
        for proc in procedures:
            # Check if a procedure with the same code already exists for the clinic
            if not DentalProcedure.objects.filter(clinic=clinic, code=proc['code']).exists():
                DentalProcedure.objects.create(
                    clinic=clinic,
                    name=proc['name'],
                    code=proc['code'],
                    description=proc['description'],
                    category=proc['category'],
                    default_price=proc['default_price'],
                    duration_minutes=proc['duration_minutes'],
                    created_at=timezone.now(),
                )

def reverse_general_procedures(apps, schema_editor):
    DentalProcedure = apps.get_model('api', 'DentalProcedure')
    # Delete the procedures backfilled by this migration
    DentalProcedure.objects.filter(code__in=["D1110", "F1234", "O5678"]).delete()

class Migration(migrations.Migration):

    dependencies = [
        # Adjust the dependency to your last migration, e.g.,
        ('api', '0019_alter_generalprocedure_options'),
    ]

    operations = [
        migrations.RunPython(create_general_procedures, reverse_general_procedures),
    ] 