from django.test import TestCase
from django.contrib.auth.models import User
from app.models import Patient, Appointment, Tooth, ToothCondition, Treatment, UserProfile
from app.forms import PatientForm, AppointmentForm, TreatmentForm
from datetime import date, time, datetime, timedelta


class PatientFormTest(TestCase):
    def test_valid_patient_form(self):
        """Test that the patient form validates with correct data"""
        form_data = {
            'name': 'Test Patient',
            'age': 30,
            'gender': 'M',
            'date_of_birth': '1993-01-01',
            'phone': '1234567890',
            'email': 'test@example.com',
            'address': '123 Test Street',
            'chief_complaint': 'Toothache',
            'medical_history': 'None',
            'drug_allergies': 'None',
            'previous_dental_work': 'None'
        }
        form = PatientForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_patient_form(self):
        """Test that the patient form fails with invalid data"""
        # Missing required fields
        form_data = {
            'name': 'Test Patient',
            # Missing age
            'gender': 'M',
            # Missing phone
            'address': '123 Test Street'
        }
        form = PatientForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('age', form.errors)
        self.assertIn('phone', form.errors)
    
    def test_patient_form_required_fields(self):
        """Test that required fields are properly enforced"""
        # Create an empty form
        form = PatientForm(data={})
        self.assertFalse(form.is_valid())
        
        # Check that required fields are in the errors
        required_fields = ['name', 'age', 'gender', 'phone']
        for field in required_fields:
            self.assertIn(field, form.errors)
            
        # Check that optional fields are not in the errors
        optional_fields = ['address', 'email', 'date_of_birth', 'chief_complaint', 'medical_history', 'drug_allergies', 'previous_dental_work']
        for field in optional_fields:
            self.assertNotIn(field, form.errors)


class AppointmentFormTest(TestCase):
    def setUp(self):
        # Create a user (dentist)
        self.user = User.objects.create_user(
            username='dentist',
            email='dentist@example.com',
            password='dentistpassword',
            first_name='Doctor',
            last_name='Dentist'
        )
        # Get the existing profile created by the signal and update it
        self.profile = UserProfile.objects.get(user=self.user)
        self.profile.role = 'dentist'
        self.profile.save()
        
        # Create a patient
        self.patient = Patient.objects.create(
            name='Jane Doe',
            age=25,
            gender='F',
            phone='9876543210',
            address='456 Patient Avenue'
        )
        
        # Create an existing appointment for overlap testing
        self.existing_appointment = Appointment.objects.create(
            patient=self.patient,
            dentist=self.user,
            date=date.today() + timedelta(days=1),  # Tomorrow
            start_time=time(10, 0),  # 10:00 AM
            end_time=time(10, 30),   # 10:30 AM
            status='scheduled'
        )
    
    def test_valid_appointment_form(self):
        """Test that the appointment form validates with correct data"""
        form_data = {
            'patient': self.patient.id,
            'dentist': self.user.id,
            'date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),  # Tomorrow
            'start_time': '09:00',  # 9:00 AM (before existing appointment)
            'duration': 30,
            'notes': 'Regular checkup',
            'chief_complaint': 'Toothache'
        }
        form = AppointmentForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_appointment_form(self):
        """Test that the appointment form fails with invalid data"""
        # Missing required fields
        form_data = {
            # Missing patient
            'dentist': self.user.id,
            # Missing date
            'start_time': '09:00',
            'duration': 30
        }
        form = AppointmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('patient', form.errors)
        self.assertIn('date', form.errors)
    
    def test_end_time_calculation(self):
        """Test that end_time is correctly calculated from start_time and duration"""
        form_data = {
            'patient': self.patient.id,
            'dentist': self.user.id,
            'date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'start_time': '09:00',
            'duration': 45,  # 45 minutes
            'notes': 'Extended checkup'
        }
        form = AppointmentForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save the form to get the instance with calculated end_time
        appointment = form.save()
        
        # Check that end_time is 45 minutes after start_time
        expected_end_time = time(9, 45)  # 9:45 AM
        self.assertEqual(appointment.end_time, expected_end_time)
    
    def test_overlapping_appointment_validation(self):
        """Test that overlapping appointments are detected and rejected"""
        # Create a form with an appointment that overlaps with existing_appointment
        form_data = {
            'patient': self.patient.id,
            'dentist': self.user.id,
            'date': (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),  # Same day as existing
            'start_time': '10:15',  # 10:15 AM (overlaps with 10:00-10:30)
            'duration': 30,
            'notes': 'This should fail due to overlap'
        }
        form = AppointmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Check that there's a non-field error about overlapping
        self.assertTrue(any('overlaps' in error for error in form.non_field_errors()))


class TreatmentFormTest(TestCase):
    def setUp(self):
        # Create a patient
        self.patient = Patient.objects.create(
            name='Bob Smith',
            age=40,
            gender='M',
            phone='5551234567',
            address='789 Patient Road'
        )
        
        # Create a dentist
        self.dentist = User.objects.create_user(
            username='drdentist',
            email='dr@example.com',
            password='drpassword'
        )
        
        # Get the existing profile created by the signal and update it
        self.profile = UserProfile.objects.get(user=self.dentist)
        self.profile.role = 'dentist'
        self.profile.save()
        
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
        
        # Create an appointment for this patient
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            dentist=self.dentist,
            date=date.today(),
            start_time=time(14, 0),
            end_time=time(15, 0),
            status='scheduled'
        )
        
        # Create an appointment for another patient (should not appear in form)
        self.other_patient = Patient.objects.create(
            name='Other Patient',
            age=50,
            gender='F',
            phone='5559876543',
            address='Other Address'
        )
        
        self.other_appointment = Appointment.objects.create(
            patient=self.other_patient,
            dentist=self.dentist,
            date=date.today(),
            start_time=time(16, 0),
            end_time=time(17, 0),
            status='scheduled'
        )
    
    def test_valid_treatment_form(self):
        """Test that the treatment form validates with correct data"""
        form_data = {
            'tooth': self.tooth.id,
            'condition': self.condition.id,
            'appointment': self.appointment.id,
            'description': 'Crown placement',
            'status': 'planned',
            'cost': '500.00'
        }
        form = TreatmentForm(data=form_data, patient=self.patient)
        self.assertTrue(form.is_valid())
    
    def test_invalid_treatment_form(self):
        """Test that the treatment form fails with invalid data"""
        # Missing required fields
        form_data = {
            # Missing tooth (optional, so this should be fine)
            # Missing condition
            'appointment': self.appointment.id,
            'description': 'Crown placement',
            'status': 'planned',
            'cost': '500.00'
        }
        form = TreatmentForm(data=form_data, patient=self.patient)
        self.assertFalse(form.is_valid())
        self.assertIn('condition', form.errors)
    
    def test_appointment_filtering_by_patient(self):
        """Test that appointments are filtered to only show those for the patient"""
        form = TreatmentForm(patient=self.patient)
        
        # Check that the appointment queryset only contains appointments for this patient
        appointment_choices = form.fields['appointment'].queryset
        
        # The patient's appointment should be in the choices
        self.assertIn(self.appointment, appointment_choices)
        
        # The other patient's appointment should not be in the choices
        self.assertNotIn(self.other_appointment, appointment_choices) 