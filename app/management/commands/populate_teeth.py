from django.core.management.base import BaseCommand
from app.models import Tooth, ToothCondition

class Command(BaseCommand):
    help = 'Populates the database with teeth data using Zsigmondy-Palmer notation'

    def handle(self, *args, **options):
        # Clear existing teeth data
        Tooth.objects.all().delete()
        
        # Upper teeth (1-16)
        upper_teeth = [
            (1, 'Upper Right Third Molar'),
            (2, 'Upper Right Second Molar'),
            (3, 'Upper Right First Molar'),
            (4, 'Upper Right Second Premolar'),
            (5, 'Upper Right First Premolar'),
            (6, 'Upper Right Canine'),
            (7, 'Upper Right Lateral Incisor'),
            (8, 'Upper Right Central Incisor'),
            (9, 'Upper Left Central Incisor'),
            (10, 'Upper Left Lateral Incisor'),
            (11, 'Upper Left Canine'),
            (12, 'Upper Left First Premolar'),
            (13, 'Upper Left Second Premolar'),
            (14, 'Upper Left First Molar'),
            (15, 'Upper Left Second Molar'),
            (16, 'Upper Left Third Molar'),
        ]
        
        # Lower teeth (17-32)
        lower_teeth = [
            (17, 'Lower Left Third Molar'),
            (18, 'Lower Left Second Molar'),
            (19, 'Lower Left First Molar'),
            (20, 'Lower Left Second Premolar'),
            (21, 'Lower Left First Premolar'),
            (22, 'Lower Left Canine'),
            (23, 'Lower Left Lateral Incisor'),
            (24, 'Lower Left Central Incisor'),
            (25, 'Lower Right Central Incisor'),
            (26, 'Lower Right Lateral Incisor'),
            (27, 'Lower Right Canine'),
            (28, 'Lower Right First Premolar'),
            (29, 'Lower Right Second Premolar'),
            (30, 'Lower Right First Molar'),
            (31, 'Lower Right Second Molar'),
            (32, 'Lower Right Third Molar'),
        ]
        
        # Create teeth
        for number, name in upper_teeth + lower_teeth:
            Tooth.objects.create(number=number, name=name)
            self.stdout.write(self.style.SUCCESS(f'Created tooth {number}: {name}'))
        
        # Create common tooth conditions if they don't exist
        conditions = [
            'Caries', 
            'Filling', 
            'Crown', 
            'Root Canal', 
            'Extraction', 
            'Bridge', 
            'Implant',
            'Veneer',
            'Fracture',
            'Missing',
            'Impacted',
            'Sensitive',
            'Mobility',
            'Gingivitis',
            'Periodontitis'
        ]
        
        for condition in conditions:
            ToothCondition.objects.get_or_create(
                name=condition,
                defaults={'description': f'Patient has {condition.lower()} on this tooth'}
            )
            self.stdout.write(self.style.SUCCESS(f'Created condition: {condition}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully populated teeth and conditions data')) 