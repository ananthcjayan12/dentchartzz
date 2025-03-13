import os
import django
import uuid

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from app.models import UserProfile, Tooth, ToothCondition

def create_superuser():
    """Create a superuser if it doesn't exist"""
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print(f"Superuser created: {user.username}")
    else:
        print("Superuser already exists")

def create_teeth():
    """Create teeth if they don't exist"""
    if Tooth.objects.count() == 0:
        # Upper right quadrant (1)
        for i, name in enumerate([
            "Third Molar", "Second Molar", "First Molar", "Second Premolar",
            "First Premolar", "Canine", "Lateral Incisor", "Central Incisor"
        ], 1):
            Tooth.objects.create(
                number=i,
                name=f"Upper Right {name}",
                quadrant=1,
                position=i
            )
            print(f"Created tooth: Upper Right {name}")
        
        # Upper left quadrant (2)
        for i, name in enumerate([
            "Central Incisor", "Lateral Incisor", "Canine", "First Premolar",
            "Second Premolar", "First Molar", "Second Molar", "Third Molar"
        ], 1):
            Tooth.objects.create(
                number=i + 8,
                name=f"Upper Left {name}",
                quadrant=2,
                position=i
            )
            print(f"Created tooth: Upper Left {name}")
        
        # Lower left quadrant (3)
        for i, name in enumerate([
            "Third Molar", "Second Molar", "First Molar", "Second Premolar",
            "First Premolar", "Canine", "Lateral Incisor", "Central Incisor"
        ], 1):
            Tooth.objects.create(
                number=i + 16,
                name=f"Lower Left {name}",
                quadrant=3,
                position=i
            )
            print(f"Created tooth: Lower Left {name}")
        
        # Lower right quadrant (4)
        for i, name in enumerate([
            "Central Incisor", "Lateral Incisor", "Canine", "First Premolar",
            "Second Premolar", "First Molar", "Second Molar", "Third Molar"
        ], 1):
            Tooth.objects.create(
                number=i + 24,
                name=f"Lower Right {name}",
                quadrant=4,
                position=i
            )
            print(f"Created tooth: Lower Right {name}")
    else:
        print("Teeth already exist")

def create_tooth_conditions():
    """Create tooth conditions if they don't exist"""
    conditions = [
        ("Cavity", "Dental decay requiring filling"),
        ("Fracture", "Tooth fracture requiring restoration"),
        ("Root Canal", "Endodontic treatment needed"),
        ("Crown", "Crown restoration needed"),
        ("Extraction", "Tooth extraction required"),
        ("Bridge", "Dental bridge needed"),
        ("Implant", "Dental implant needed"),
        ("Veneer", "Cosmetic veneer needed"),
        ("Cleaning", "Professional cleaning needed"),
        ("Healthy", "No treatment needed")
    ]
    
    if ToothCondition.objects.count() == 0:
        for name, description in conditions:
            ToothCondition.objects.create(
                name=name,
                description=description
            )
            print(f"Created tooth condition: {name}")
    else:
        print("Tooth conditions already exist")

def create_staff_users():
    """Create staff users if they don't exist"""
    # Create a dentist
    if not User.objects.filter(username='dentist').exists():
        dentist = User.objects.create_user(
            username='dentist',
            email='dentist@example.com',
            password='dentist123',
            first_name='Doctor',
            last_name='Dentist'
        )
        profile = UserProfile.objects.get(user=dentist)
        profile.role = 'dentist'
        profile.phone = '1234567890'
        profile.address = '123 Dentist Street'
        profile.save()
        print(f"Dentist user created: {dentist.username}")
    else:
        print("Dentist user already exists")
    
    # Create a staff member
    if not User.objects.filter(username='staff').exists():
        staff = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staff123',
            first_name='Staff',
            last_name='Member'
        )
        profile = UserProfile.objects.get(user=staff)
        profile.role = 'staff'
        profile.phone = '9876543210'
        profile.address = '456 Staff Avenue'
        profile.save()
        print(f"Staff user created: {staff.username}")
    else:
        print("Staff user already exists")

if __name__ == "__main__":
    print("Initializing database...")
    create_superuser()
    create_teeth()
    create_tooth_conditions()
    create_staff_users()
    print("Database initialization complete!") 