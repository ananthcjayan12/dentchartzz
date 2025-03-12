from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import (
    UserProfile, Patient, Appointment, Tooth, 
    ToothCondition, Treatment, TreatmentHistory
)
from datetime import date, time, datetime, timedelta
import json
import uuid


class PatientRegistrationAndAppointmentFlowTest(TestCase):
    """Test the complete flow of patient registration and appointment booking"""
    
    def setUp(self):
        self.client = Client()
        
        # Create a dentist user with unique username
        dentist_username = f"dentist_{uuid.uuid4().hex[:8]}"
        self.dentist = User.objects.create_user(
            username=dentist_username,
            email=f'{dentist_username}@example.com',
            password='dentistpassword',
            first_name='Doctor',
            last_name='Dentist'
        )
        # Get the existing profile created by the signal and update it
        self.dentist_profile = UserProfile.objects.get(user=self.dentist)
        self.dentist_profile.role = 'dentist'
        self.dentist_profile.save()
        
        # Login
        self.client.login(username=self.dentist.username, password='dentistpassword')
    
    def test_patient_registration_and_appointment_flow(self):
        """Test the complete flow of registering a patient and booking an appointment"""
        
        # Step 1: Create a new patient
        patient_data = {
            'name': 'Integration Test Patient',
            'age': 35,
            'gender': 'M',
            'date_of_birth': '1988-01-01',
            'phone': '5551234567',
            'email': 'integration@example.com',
            'address': '123 Integration Street',
            'chief_complaint': 'Toothache and sensitivity',
            'medical_history': 'None',
            'drug_allergies': 'None',
            'previous_dental_work': 'Fillings'
        }
        
        response = self.client.post(reverse('patient_create'), patient_data)
        
        # Check that a new patient was created
        self.assertEqual(Patient.objects.count(), 1)
        patient = Patient.objects.first()
        self.assertEqual(patient.name, 'Integration Test Patient')
        
        # Step 2: Book an appointment for the patient
        tomorrow = date.today() + timedelta(days=1)
        appointment_data = {
            'patient': patient.id,
            'dentist': self.dentist.id,
            'date': tomorrow.strftime('%Y-%m-%d'),
            'start_time': '10:00',
            'duration': 30,
            'notes': 'Initial consultation',
            'chief_complaint': 'Toothache and sensitivity'
        }
        
        response = self.client.post(reverse('appointment_create'), appointment_data)
        
        # Check that an appointment was created
        self.assertEqual(Appointment.objects.count(), 1)
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.patient, patient)
        self.assertEqual(appointment.dentist, self.dentist)
        self.assertEqual(appointment.start_time, time(10, 0))
        self.assertEqual(appointment.end_time, time(10, 30))
        
        # Step 3: View the appointment details
        response = self.client.get(reverse('appointment_detail', kwargs={'pk': appointment.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/appointment_detail.html')
        
        # Step 4: Update the appointment status to completed
        response = self.client.post(
            reverse('appointment_status_update', kwargs={'pk': appointment.pk}),
            {'status': 'completed'}
        )
        
        # Refresh the appointment from the database
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'completed')


class TreatmentPlanningAndUpdatingFlowTest(TestCase):
    """Test the complete flow of treatment planning and updating"""
    
    def setUp(self):
        self.client = Client()
        
        # Create a dentist user with unique username
        dentist_username = f"dentist_{uuid.uuid4().hex[:8]}"
        self.dentist = User.objects.create_user(
            username=dentist_username,
            email=f'{dentist_username}@example.com',
            password='dentistpassword'
        )
        # Get the existing profile created by the signal and update it
        self.dentist_profile = UserProfile.objects.get(user=self.dentist)
        self.dentist_profile.role = 'dentist'
        self.dentist_profile.save()
        
        # Create a patient
        self.patient = Patient.objects.create(
            name='Treatment Flow Patient',
            age=40,
            gender='M',
            phone='5559876543',
            address='456 Treatment Street',
            chief_complaint='Pain in lower left molar'
        )
        
        # Create a tooth
        self.tooth = Tooth.objects.create(
            number=36,
            name='Lower Left First Molar',
            quadrant=3,
            position=6
        )
        
        # Create a condition
        self.condition = ToothCondition.objects.create(
            name='Deep Cavity',
            description='Deep dental decay possibly affecting pulp'
        )
        
        # Create an appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            dentist=self.dentist,
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status='scheduled'
        )
        
        # Login
        self.client.login(username=self.dentist.username, password='dentistpassword')
    
    def test_treatment_planning_and_updating_flow(self):
        """Test the complete flow of planning and updating a treatment"""
        
        # Step 1: View the dental chart
        response = self.client.get(reverse('dental_chart', kwargs={'patient_id': self.patient.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/dental_chart.html')
        
        # Step 2: Add a treatment
        treatment_data = {
            'tooth_ids': str(self.tooth.id),
            'condition': self.condition.id,
            'appointment': self.appointment.id,
            'description': 'Root canal treatment needed',
            'status': 'planned',
            'cost': '800.00'
        }
        
        response = self.client.post(
            reverse('add_treatment', kwargs={'patient_id': self.patient.id}),
            treatment_data
        )
        
        # Check that a treatment was created
        self.assertEqual(Treatment.objects.count(), 1)
        treatment = Treatment.objects.first()
        self.assertEqual(treatment.patient, self.patient)
        self.assertEqual(treatment.tooth, self.tooth)
        self.assertEqual(treatment.condition, self.condition)
        self.assertEqual(treatment.status, 'planned')
        
        # Step 3: View the treatment details
        response = self.client.get(reverse('treatment_detail', kwargs={'pk': treatment.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/treatment_detail.html')
        
        # Step 4: Update the treatment status to in_progress
        updated_data = {
            'tooth': self.tooth.id,
            'condition': self.condition.id,
            'appointment': self.appointment.id,
            'description': 'Root canal treatment in progress',
            'status': 'in_progress',
            'cost': '800.00'
        }
        
        response = self.client.post(
            reverse('treatment_update', kwargs={'pk': treatment.pk}),
            updated_data
        )
        
        # Refresh the treatment from the database
        treatment.refresh_from_db()
        self.assertEqual(treatment.status, 'in_progress')
        self.assertEqual(treatment.description, 'Root canal treatment in progress')
        
        # Check that a treatment history entry was created
        self.assertEqual(TreatmentHistory.objects.count(), 1)
        history = TreatmentHistory.objects.first()
        self.assertEqual(history.treatment, treatment)
        self.assertEqual(history.previous_status, 'planned')
        self.assertEqual(history.new_status, 'in_progress')
        
        # Step 5: Update the treatment status to completed
        updated_data = {
            'tooth': self.tooth.id,
            'condition': self.condition.id,
            'appointment': self.appointment.id,
            'description': 'Root canal treatment completed',
            'status': 'completed',
            'cost': '800.00'
        }
        
        response = self.client.post(
            reverse('treatment_update', kwargs={'pk': treatment.pk}),
            updated_data
        )
        
        # Refresh the treatment from the database
        treatment.refresh_from_db()
        self.assertEqual(treatment.status, 'completed')
        self.assertEqual(treatment.description, 'Root canal treatment completed')
        
        # Check that another treatment history entry was created
        self.assertEqual(TreatmentHistory.objects.count(), 2)
        history = TreatmentHistory.objects.latest('created_at')
        self.assertEqual(history.treatment, treatment)
        self.assertEqual(history.previous_status, 'in_progress')
        self.assertEqual(history.new_status, 'completed')


class AppointmentSchedulingAndManagementFlowTest(TestCase):
    """Test the complete flow of appointment scheduling and management"""
    
    def setUp(self):
        self.client = Client()
        
        # Create a dentist user with unique username
        dentist_username = f"dentist_{uuid.uuid4().hex[:8]}"
        self.dentist = User.objects.create_user(
            username=dentist_username,
            email=f'{dentist_username}@example.com',
            password='dentistpassword'
        )
        # Get the existing profile created by the signal and update it
        self.dentist_profile = UserProfile.objects.get(user=self.dentist)
        self.dentist_profile.role = 'dentist'
        self.dentist_profile.save()
        
        # Create a patient
        self.patient = Patient.objects.create(
            name='Appointment Flow Patient',
            age=30,
            gender='F',
            phone='5551112222',
            address='789 Appointment Street',
            chief_complaint='Regular checkup'
        )
        
        # Login
        self.client.login(username=self.dentist.username, password='dentistpassword')
    
    def test_appointment_scheduling_and_management_flow(self):
        """Test the complete flow of scheduling and managing appointments"""
        
        # Step 1: Check available time slots
        tomorrow = date.today() + timedelta(days=1)
        response = self.client.get(
            reverse('get_time_slots') + 
            f'?date={tomorrow.strftime("%Y-%m-%d")}&dentist={self.dentist.id}'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('time_slots', data)
        
        # Step 2: Book an appointment
        appointment_data = {
            'patient': self.patient.id,
            'dentist': self.dentist.id,
            'date': tomorrow.strftime('%Y-%m-%d'),
            'start_time': '14:00',  # 2:00 PM
            'duration': 30,
            'notes': 'Regular checkup',
            'chief_complaint': 'Regular checkup'
        }
        
        response = self.client.post(reverse('appointment_create'), appointment_data)
        
        # Check that an appointment was created
        self.assertEqual(Appointment.objects.count(), 1)
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.patient, self.patient)
        self.assertEqual(appointment.start_time, time(14, 0))
        
        # Step 3: Check the appointment calendar
        response = self.client.get(reverse('appointment_calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/appointment_calendar.html')
        
        # Step 4: Reschedule the appointment
        updated_data = {
            'patient': self.patient.id,
            'dentist': self.dentist.id,
            'date': tomorrow.strftime('%Y-%m-%d'),
            'start_time': '15:00',  # 3:00 PM
            'duration': 45,  # Extended duration
            'notes': 'Rescheduled checkup',
            'chief_complaint': 'Regular checkup'
        }
        
        response = self.client.post(
            reverse('appointment_update', kwargs={'pk': appointment.pk}),
            updated_data
        )
        
        # Refresh the appointment from the database
        appointment.refresh_from_db()
        self.assertEqual(appointment.start_time, time(15, 0))
        self.assertEqual(appointment.end_time, time(15, 45))
        # Check that notes contains the expected text (allowing for chief complaint to be appended)
        self.assertIn('Rescheduled checkup', appointment.notes)
        
        # Step 5: Cancel the appointment
        response = self.client.post(reverse('appointment_cancel', kwargs={'pk': appointment.pk}))
        
        # Refresh the appointment from the database
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'cancelled')
        
        # Step 6: Book a new appointment
        new_appointment_data = {
            'patient': self.patient.id,
            'dentist': self.dentist.id,
            'date': (tomorrow + timedelta(days=1)).strftime('%Y-%m-%d'),  # Day after tomorrow
            'start_time': '10:00',  # 10:00 AM
            'duration': 30,
            'notes': 'New appointment after cancellation',
            'chief_complaint': 'Regular checkup'
        }
        
        response = self.client.post(reverse('appointment_create'), new_appointment_data)
        
        # Check that a new appointment was created
        self.assertEqual(Appointment.objects.count(), 2)
        new_appointment = Appointment.objects.latest('created_at')
        self.assertEqual(new_appointment.patient, self.patient)
        self.assertEqual(new_appointment.start_time, time(10, 0))
        self.assertEqual(new_appointment.status, 'scheduled') 