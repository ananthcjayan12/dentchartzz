from django.core.management.base import BaseCommand
from app.models import Tooth, ToothCondition

class Command(BaseCommand):
    help = 'Populates the database with teeth data using quadrant-based tooth numbering system'

    def handle(self, *args, **options):
        # Clear existing teeth data
        Tooth.objects.all().delete()
        
        # Define teeth by quadrant
        # Format: (double_digit_number, number_in_quadrant, quadrant, name)
        # Quadrants: 1=upper right, 2=upper left, 3=lower left, 4=lower right
        teeth_data = [
            # Upper Right (Quadrant 1)
            (18, 8, 1, 'Upper Right Third Molar'),
            (17, 7, 1, 'Upper Right Second Molar'),
            (16, 6, 1, 'Upper Right First Molar'),
            (15, 5, 1, 'Upper Right Second Premolar'),
            (14, 4, 1, 'Upper Right First Premolar'),
            (13, 3, 1, 'Upper Right Canine'),
            (12, 2, 1, 'Upper Right Lateral Incisor'),
            (11, 1, 1, 'Upper Right Central Incisor'),
            
            # Upper Left (Quadrant 2)
            (21, 1, 2, 'Upper Left Central Incisor'),
            (22, 2, 2, 'Upper Left Lateral Incisor'),
            (23, 3, 2, 'Upper Left Canine'),
            (24, 4, 2, 'Upper Left First Premolar'),
            (25, 5, 2, 'Upper Left Second Premolar'),
            (26, 6, 2, 'Upper Left First Molar'),
            (27, 7, 2, 'Upper Left Second Molar'),
            (28, 8, 2, 'Upper Left Third Molar'),
            
            # Lower Left (Quadrant 3)
            (38, 8, 3, 'Lower Left Third Molar'),
            (37, 7, 3, 'Lower Left Second Molar'),
            (36, 6, 3, 'Lower Left First Molar'),
            (35, 5, 3, 'Lower Left Second Premolar'),
            (34, 4, 3, 'Lower Left First Premolar'),
            (33, 3, 3, 'Lower Left Canine'),
            (32, 2, 3, 'Lower Left Lateral Incisor'),
            (31, 1, 3, 'Lower Left Central Incisor'),
            
            # Lower Right (Quadrant 4)
            (41, 1, 4, 'Lower Right Central Incisor'),
            (42, 2, 4, 'Lower Right Lateral Incisor'),
            (43, 3, 4, 'Lower Right Canine'),
            (44, 4, 4, 'Lower Right First Premolar'),
            (45, 5, 4, 'Lower Right Second Premolar'),
            (46, 6, 4, 'Lower Right First Molar'),
            (47, 7, 4, 'Lower Right Second Molar'),
            (48, 8, 4, 'Lower Right Third Molar'),
        ]
        
        # Create teeth
        for number, position, quadrant, name in teeth_data:
            Tooth.objects.create(
                number=number,
                name=name,
                quadrant=quadrant,
                position=position
            )
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