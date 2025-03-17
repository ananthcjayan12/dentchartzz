from django.db import migrations
from django.utils import timezone

def add_standard_dental_conditions(apps, schema_editor):
    """Add standard dental conditions to all clinics."""
    Clinic = apps.get_model('api', 'Clinic')
    DentalCondition = apps.get_model('api', 'DentalCondition')
    
    # Standard conditions to add
    standard_conditions = [
        {
            'name': 'Cavity',
            'code': 'C01',
            'description': 'Tooth decay or cavity',
            'color_code': '#FF0000',
            'icon': 'cavity-icon',
        },
        {
            'name': 'Fracture',
            'code': 'F01',
            'description': 'Tooth fracture or crack',
            'color_code': '#FFA500',
            'icon': 'fracture-icon',
        },
        {
            'name': 'Missing',
            'code': 'M01',
            'description': 'Missing tooth',
            'color_code': '#000000',
            'icon': 'missing-icon',
        },
        {
            'name': 'Impacted',
            'code': 'I01',
            'description': 'Impacted tooth',
            'color_code': '#800080',
            'icon': 'impacted-icon',
        },
        {
            'name': 'Root Canal',
            'code': 'RC01',
            'description': 'Root canal treated tooth',
            'color_code': '#0000FF',
            'icon': 'root-canal-icon',
        },
        {
            'name': 'Crown',
            'code': 'CR01',
            'description': 'Tooth with crown',
            'color_code': '#FFD700',
            'icon': 'crown-icon',
        },
        {
            'name': 'Bridge',
            'code': 'BR01',
            'description': 'Bridge abutment tooth',
            'color_code': '#A52A2A',
            'icon': 'bridge-icon',
        },
        {
            'name': 'Implant',
            'code': 'IM01',
            'description': 'Dental implant',
            'color_code': '#808080',
            'icon': 'implant-icon',
        },
        {
            'name': 'Veneer',
            'code': 'V01',
            'description': 'Tooth with veneer',
            'color_code': '#FFFFFF',
            'icon': 'veneer-icon',
        },
        {
            'name': 'Gingivitis',
            'code': 'G01',
            'description': 'Gum inflammation',
            'color_code': '#FF69B4',
            'icon': 'gingivitis-icon',
        }
    ]
    
    # Add conditions to all clinics
    for clinic in Clinic.objects.all():
        for condition_data in standard_conditions:
            DentalCondition.objects.get_or_create(
                clinic=clinic,
                code=condition_data['code'],
                defaults={
                    **condition_data,
                    'is_standard': True,
                    'created_at': timezone.now()
                }
            )

def add_standard_dental_procedures(apps, schema_editor):
    """Add standard dental procedures to all clinics."""
    Clinic = apps.get_model('api', 'Clinic')
    DentalProcedure = apps.get_model('api', 'DentalProcedure')
    
    # Standard procedures to add
    standard_procedures = [
        {
            'name': 'Amalgam Filling (1 surface)',
            'code': 'D2140',
            'description': 'Silver filling for posterior teeth (1 surface)',
            'category': 'restorative',
            'default_price': 120.00,
            'duration_minutes': 30,
        },
        {
            'name': 'Composite Filling (1 surface)',
            'code': 'D2330',
            'description': 'Tooth-colored filling for anterior teeth (1 surface)',
            'category': 'restorative',
            'default_price': 150.00,
            'duration_minutes': 30,
        },
        {
            'name': 'Composite Filling (2 surfaces)',
            'code': 'D2331',
            'description': 'Tooth-colored filling for anterior teeth (2 surfaces)',
            'category': 'restorative',
            'default_price': 180.00,
            'duration_minutes': 45,
        },
        {
            'name': 'Root Canal - Anterior',
            'code': 'D3310',
            'description': 'Root canal therapy for anterior tooth',
            'category': 'endodontic',
            'default_price': 700.00,
            'duration_minutes': 60,
        },
        {
            'name': 'Root Canal - Premolar',
            'code': 'D3320',
            'description': 'Root canal therapy for premolar tooth',
            'category': 'endodontic',
            'default_price': 800.00,
            'duration_minutes': 75,
        },
        {
            'name': 'Root Canal - Molar',
            'code': 'D3330',
            'description': 'Root canal therapy for molar tooth',
            'category': 'endodontic',
            'default_price': 1000.00,
            'duration_minutes': 90,
        },
        {
            'name': 'Extraction - Simple',
            'code': 'D7140',
            'description': 'Simple extraction of erupted tooth',
            'category': 'oral surgery',
            'default_price': 150.00,
            'duration_minutes': 30,
        },
        {
            'name': 'Extraction - Surgical',
            'code': 'D7210',
            'description': 'Surgical extraction of erupted tooth',
            'category': 'oral surgery',
            'default_price': 250.00,
            'duration_minutes': 45,
        },
        {
            'name': 'Crown - Porcelain/Ceramic',
            'code': 'D2740',
            'description': 'Porcelain/ceramic crown',
            'category': 'prosthodontic',
            'default_price': 1200.00,
            'duration_minutes': 60,
        },
        {
            'name': 'Scaling and Root Planing (per quadrant)',
            'code': 'D4341',
            'description': 'Deep cleaning for periodontal disease',
            'category': 'periodontic',
            'default_price': 200.00,
            'duration_minutes': 45,
        }
    ]
    
    # Add procedures to all clinics
    for clinic in Clinic.objects.all():
        for procedure_data in standard_procedures:
            DentalProcedure.objects.get_or_create(
                clinic=clinic,
                code=procedure_data['code'],
                defaults={
                    **procedure_data,
                    'is_standard': True,
                    'created_at': timezone.now()
                }
            )

def remove_standard_dental_conditions(apps, schema_editor):
    """Remove standard dental conditions."""
    DentalCondition = apps.get_model('api', 'DentalCondition')
    DentalCondition.objects.filter(is_standard=True).delete()

def remove_standard_dental_procedures(apps, schema_editor):
    """Remove standard dental procedures."""
    DentalProcedure = apps.get_model('api', 'DentalProcedure')
    DentalProcedure.objects.filter(is_standard=True).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0006_dentalcondition_created_at_and_more'),
    ]

    operations = [
        migrations.RunPython(add_standard_dental_conditions, remove_standard_dental_conditions),
        migrations.RunPython(add_standard_dental_procedures, remove_standard_dental_procedures),
    ]