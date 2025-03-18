from django.db import migrations

def create_primary_teeth(apps, schema_editor):
    DentalChartTooth = apps.get_model('api', 'DentalChartTooth')
    Patient = apps.get_model('api', 'Patient')
    
    primary_teeth_data = [
        # Upper Right
        {'number': 'A', 'universal_number': 51, 'name': 'Primary Upper Right Central Incisor', 'quadrant': 'upper_right'},
        {'number': 'B', 'universal_number': 52, 'name': 'Primary Upper Right Lateral Incisor', 'quadrant': 'upper_right'},
        {'number': 'C', 'universal_number': 53, 'name': 'Primary Upper Right Canine', 'quadrant': 'upper_right'},
        {'number': 'D', 'universal_number': 54, 'name': 'Primary Upper Right First Molar', 'quadrant': 'upper_right'},
        {'number': 'E', 'universal_number': 55, 'name': 'Primary Upper Right Second Molar', 'quadrant': 'upper_right'},
        # Upper Left
        {'number': 'F', 'universal_number': 61, 'name': 'Primary Upper Left Central Incisor', 'quadrant': 'upper_left'},
        {'number': 'G', 'universal_number': 62, 'name': 'Primary Upper Left Lateral Incisor', 'quadrant': 'upper_left'},
        {'number': 'H', 'universal_number': 63, 'name': 'Primary Upper Left Canine', 'quadrant': 'upper_left'},
        {'number': 'I', 'universal_number': 64, 'name': 'Primary Upper Left First Molar', 'quadrant': 'upper_left'},
        {'number': 'J', 'universal_number': 65, 'name': 'Primary Upper Left Second Molar', 'quadrant': 'upper_left'},
        # Lower Left
        {'number': 'K', 'universal_number': 71, 'name': 'Primary Lower Left Central Incisor', 'quadrant': 'lower_left'},
        {'number': 'L', 'universal_number': 72, 'name': 'Primary Lower Left Lateral Incisor', 'quadrant': 'lower_left'},
        {'number': 'M', 'universal_number': 73, 'name': 'Primary Lower Left Canine', 'quadrant': 'lower_left'},
        {'number': 'N', 'universal_number': 74, 'name': 'Primary Lower Left First Molar', 'quadrant': 'lower_left'},
        {'number': 'O', 'universal_number': 75, 'name': 'Primary Lower Left Second Molar', 'quadrant': 'lower_left'},
        # Lower Right
        {'number': 'P', 'universal_number': 81, 'name': 'Primary Lower Right Central Incisor', 'quadrant': 'lower_right'},
        {'number': 'Q', 'universal_number': 82, 'name': 'Primary Lower Right Lateral Incisor', 'quadrant': 'lower_right'},
        {'number': 'R', 'universal_number': 83, 'name': 'Primary Lower Right Canine', 'quadrant': 'lower_right'},
        {'number': 'S', 'universal_number': 84, 'name': 'Primary Lower Right First Molar', 'quadrant': 'lower_right'},
        {'number': 'T', 'universal_number': 85, 'name': 'Primary Lower Right Second Molar', 'quadrant': 'lower_right'},
    ]
    
    # Add primary teeth for each patient
    for patient in Patient.objects.all():
        for tooth_data in primary_teeth_data:
            DentalChartTooth.objects.create(
                patient=patient,
                dentition_type='primary',
                **tooth_data
            )

def remove_primary_teeth(apps, schema_editor):
    DentalChartTooth = apps.get_model('api', 'DentalChartTooth')
    DentalChartTooth.objects.filter(dentition_type='primary').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_alter_dentalcharttooth_unique_together_and_more'),
    ]

    operations = [
        migrations.RunPython(create_primary_teeth, remove_primary_teeth),
    ]