import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from app.models import (
    UserProfile, Patient, Appointment, Tooth, 
    ToothCondition, Treatment, TreatmentHistory
)
from datetime import date, time, datetime, timedelta
from django.core.exceptions import ValidationError
import uuid


@pytest.mark.django_db
class TestUserProfile:
    @pytest.fixture
    def user_profile(self):
        username = f"testuser_{uuid.uuid4().hex[:8]}"
        user = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='testpassword'
        )
        
        # Get the profile that was automatically created by the signal
        profile = UserProfile.objects.get(user=user)
        
        # Update the profile
        profile.role = 'dentist'
        profile.phone = '1234567890'
        profile.address = '123 Test Street'
        profile.save()
        
        return user, profile

    def test_profile_creation(self, user_profile):
        """Test that a user profile can be created with valid data"""
        user, profile = user_profile
        assert profile.user.username == user.username
        assert profile.role == 'dentist'
        assert profile.phone == '1234567890'
        assert profile.address == '123 Test Street'

    def test_profile_str_representation(self, user_profile):
        """Test the string representation of a user profile"""
        user, profile = user_profile
        expected_str = f"{user.username} - Dentist"
        assert str(profile) == expected_str

    def test_user_profile_relationship(self, user_profile):
        """Test the relationship between User and UserProfile"""
        user, profile = user_profile
        assert user.profile == profile


class PatientModelTest(TestCase):
    def setUp(self):
        self.patient = Patient.objects.create(
            name='John Doe',
            age=30,
            gender='M',
            date_of_birth=date(1993, 1, 1),
            phone='1234567890',
            email='john@example.com',
            address='123 Patient Street',
            chief_complaint='Toothache',
            medical_history='None',
            drug_allergies='None',
            previous_dental_work='Fillings'
        )

    def test_patient_creation(self):
        """Test that a patient can be created with valid data"""
        self.assertEqual(self.patient.name, 'John Doe')
        self.assertEqual(self.patient.age, 30)
        self.assertEqual(self.patient.gender, 'M')
        self.assertEqual(self.patient.date_of_birth, date(1993, 1, 1))
        self.assertEqual(self.patient.phone, '1234567890')
        self.assertEqual(self.patient.email, 'john@example.com')
        self.assertEqual(self.patient.address, '123 Patient Street')
        self.assertEqual(self.patient.chief_complaint, 'Toothache')
        self.assertEqual(self.patient.medical_history, 'None')
        self.assertEqual(self.patient.drug_allergies, 'None')
        self.assertEqual(self.patient.previous_dental_work, 'Fillings')

    def test_patient_str_representation(self):
        """Test the string representation of a patient"""
        self.assertEqual(str(self.patient), 'John Doe')

    def test_patient_required_fields(self):
        """Test that required fields are enforced"""
        # Create a patient with missing required fields
        patient = Patient(
            # Missing name
            age=30,
            gender='M',
            # Missing phone
            address='123 Patient Street'
        )
        
        # Validate the model
        with self.assertRaises(ValidationError):
            patient.full_clean()


@pytest.mark.django_db
class TestAppointment:
    @pytest.fixture
    def appointment_setup(self):
        # Create a user (dentist) with unique username
        username = f"dentist_{uuid.uuid4().hex[:8]}"
        user = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='dentistpassword'
        )
        
        # Get the profile that was automatically created by the signal
        profile = UserProfile.objects.get(user=user)
        
        # Update the profile
        profile.role = 'dentist'
        profile.save()
        
        # Create a patient
        patient = Patient.objects.create(
            name='Jane Doe',
            age=25,
            gender='F',
            phone='9876543210',
            address='456 Patient Avenue'
        )
        
        # Create an appointment
        appointment = Appointment.objects.create(
            patient=patient,
            dentist=user,
            date=date.today(),
            start_time=time(9, 0),  # 9:00 AM
            end_time=time(9, 30),   # 9:30 AM
            status='scheduled',
            notes='Regular checkup'
        )
        
        return user, patient, appointment

    def test_appointment_creation(self, appointment_setup):
        """Test that an appointment can be created with valid data"""
        user, patient, appointment = appointment_setup
        assert appointment.patient == patient
        assert appointment.dentist == user
        assert appointment.date == date.today()
        assert appointment.start_time == time(9, 0)
        assert appointment.end_time == time(9, 30)
        assert appointment.status == 'scheduled'
        assert appointment.notes == 'Regular checkup'

    def test_appointment_str_representation(self, appointment_setup):
        """Test the string representation of an appointment"""
        user, patient, appointment = appointment_setup
        expected_str = f"{patient.name} - {date.today()} {time(9, 0)}"
        assert str(appointment) == expected_str

    def test_appointment_duration(self, appointment_setup):
        """Test the duration calculation property"""
        user, patient, appointment = appointment_setup
        assert appointment.duration == 30
        
        # Test appointment spanning to next day
        late_appointment = Appointment.objects.create(
            patient=patient,
            dentist=user,
            date=date.today(),
            start_time=time(23, 45),  # 11:45 PM
            end_time=time(0, 15),     # 12:15 AM (next day)
            status='scheduled'
        )
        assert late_appointment.duration == 30

    def test_appointment_status_choices(self, appointment_setup):
        """Test that appointment status choices are enforced"""
        user, patient, appointment = appointment_setup
        # Valid status
        appointment.status = 'completed'
        appointment.save()
        assert appointment.status == 'completed'
        
        # Invalid status should raise an error when validating
        appointment.status = 'invalid_status'
        with pytest.raises(ValidationError):
            appointment.full_clean()


class ToothModelTest(TestCase):
    def setUp(self):
        self.tooth = Tooth.objects.create(
            number=11,
            name='Upper Right Central Incisor',
            quadrant=1,
            position=1
        )

    def test_tooth_creation(self):
        """Test that a tooth can be created with valid data"""
        self.assertEqual(self.tooth.number, 11)
        self.assertEqual(self.tooth.name, 'Upper Right Central Incisor')
        self.assertEqual(self.tooth.quadrant, 1)
        self.assertEqual(self.tooth.position, 1)

    def test_tooth_str_representation(self):
        """Test the string representation of a tooth"""
        expected_str = f"Tooth {self.tooth.number} - {self.tooth.name}"
        self.assertEqual(str(self.tooth), expected_str)


class ToothConditionModelTest(TestCase):
    def setUp(self):
        self.condition = ToothCondition.objects.create(
            name='Cavity',
            description='Dental decay requiring filling'
        )

    def test_condition_creation(self):
        """Test that a tooth condition can be created with valid data"""
        self.assertEqual(self.condition.name, 'Cavity')
        self.assertEqual(self.condition.description, 'Dental decay requiring filling')

    def test_condition_str_representation(self):
        """Test the string representation of a tooth condition"""
        self.assertEqual(str(self.condition), 'Cavity')


class TreatmentModelTest(TestCase):
    def setUp(self):
        # Create a patient
        self.patient = Patient.objects.create(
            name='Bob Smith',
            age=40,
            gender='M',
            phone='5551234567',
            address='789 Patient Road'
        )
        
        # Create a dentist with unique username
        username = f"drdentist_{uuid.uuid4().hex[:8]}"
        self.dentist = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='drpassword'
        )
        
        # Get the profile that was automatically created by the signal
        profile = UserProfile.objects.get(user=self.dentist)
        
        # Update the profile
        profile.role = 'dentist'
        profile.save()
        
        # Create a tooth
        self.tooth = Tooth.objects.create(
            number=21,
            name='Upper Left Central Incisor',
            quadrant=2,
            position=1
        )
        
        # Create a condition
        self.condition = ToothCondition.objects.create(
            name='Fracture',
            description='Tooth fracture requiring crown'
        )
        
        # Create an appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            dentist=self.dentist,
            date=date.today(),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status='scheduled'
        )
        
        # Create a treatment
        self.treatment = Treatment.objects.create(
            patient=self.patient,
            tooth=self.tooth,
            condition=self.condition,
            appointment=self.appointment,
            description='Crown placement',
            status='planned',
            cost=500.00
        )

    def test_treatment_creation(self):
        """Test that a treatment can be created with valid data"""
        self.assertEqual(self.treatment.patient, self.patient)
        self.assertEqual(self.treatment.tooth, self.tooth)
        self.assertEqual(self.treatment.condition, self.condition)
        self.assertEqual(self.treatment.appointment, self.appointment)
        self.assertEqual(self.treatment.description, 'Crown placement')
        self.assertEqual(self.treatment.status, 'planned')
        self.assertEqual(self.treatment.cost, 500.00)

    def test_treatment_str_representation(self):
        """Test the string representation of a treatment"""
        expected_str = f"{self.patient.name} - Tooth {self.tooth.number} - {self.condition.name}"
        self.assertEqual(str(self.treatment), expected_str)

    def test_treatment_relationships(self):
        """Test the relationships between Treatment and related models"""
        self.assertEqual(self.treatment.patient, self.patient)
        self.assertEqual(self.treatment.tooth, self.tooth)
        self.assertEqual(self.treatment.condition, self.condition)
        self.assertEqual(self.treatment.appointment, self.appointment)
        
        # Test reverse relationships
        self.assertIn(self.treatment, self.patient.treatments.all())
        self.assertIn(self.treatment, self.tooth.treatments.all())
        self.assertIn(self.treatment, self.condition.treatments.all())
        self.assertIn(self.treatment, self.appointment.treatments.all())


class TreatmentHistoryModelTest(TestCase):
    def setUp(self):
        # Create a patient
        self.patient = Patient.objects.create(
            name='Alice Johnson',
            age=35,
            gender='F',
            phone='5559876543',
            address='321 Patient Lane'
        )
        
        # Create a dentist with unique username
        username = f"dralice_{uuid.uuid4().hex[:8]}"
        self.dentist = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='alicepassword'
        )
        
        # Get the profile that was automatically created by the signal
        profile = UserProfile.objects.get(user=self.dentist)
        
        # Update the profile
        profile.role = 'dentist'
        profile.save()
        
        # Create a tooth
        self.tooth = Tooth.objects.create(
            number=36,
            name='Lower Left First Molar',
            quadrant=3,
            position=6
        )
        
        # Create a condition
        self.condition = ToothCondition.objects.create(
            name='Root Canal',
            description='Endodontic treatment'
        )
        
        # Create an appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            dentist=self.dentist,
            date=date.today(),
            start_time=time(10, 0),
            end_time=time(11, 0),
            status='scheduled'
        )
        
        # Create a treatment
        self.treatment = Treatment.objects.create(
            patient=self.patient,
            tooth=self.tooth,
            condition=self.condition,
            appointment=self.appointment,
            description='Root canal treatment',
            status='planned',
            cost=800.00
        )
        
        # Create a treatment history entry
        self.history = TreatmentHistory.objects.create(
            treatment=self.treatment,
            previous_status='planned',
            new_status='in_progress',
            appointment=self.appointment,
            dentist=self.dentist,
            notes='Started root canal procedure'
        )

    def test_history_creation(self):
        """Test that a treatment history entry can be created with valid data"""
        self.assertEqual(self.history.treatment, self.treatment)
        self.assertEqual(self.history.previous_status, 'planned')
        self.assertEqual(self.history.new_status, 'in_progress')
        self.assertEqual(self.history.appointment, self.appointment)
        self.assertEqual(self.history.dentist, self.dentist)
        self.assertEqual(self.history.notes, 'Started root canal procedure')

    def test_history_str_representation(self):
        """Test the string representation of a treatment history entry"""
        expected_str = f"{self.treatment} - Status changed from Planned to In Progress"
        self.assertEqual(str(self.history), expected_str)

    def test_history_treatment_relationship(self):
        """Test the relationship between TreatmentHistory and Treatment"""
        self.assertEqual(self.history.treatment, self.treatment)
        self.assertIn(self.history, self.treatment.history.all()) 