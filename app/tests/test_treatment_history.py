import uuid
from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import (
    UserProfile, Patient, Appointment, Treatment, 
    Tooth, ToothCondition, TreatmentHistory
)

class TreatmentHistoryTrackingTest(TestCase):
    """Test that treatment history correctly tracks status changes across different appointments"""
    
    def setUp(self):
        self.client = Client()
        
        # Create a dentist user
        self.dentist = User.objects.create_user(
            username=f"dentist_{uuid.uuid4().hex[:8]}",
            password="dentistpassword",
            first_name="Doctor",
            last_name="Dentist"
        )
        # Get the profile created by signal and update it
        self.dentist_profile = UserProfile.objects.get(user=self.dentist)
        self.dentist_profile.role = 'dentist'
        self.dentist_profile.save()
        
        # Create a patient
        self.patient = Patient.objects.create(
            name='History Test Patient',
            age=45,
            gender='F',
            phone='5551234567',
            address='123 Test Street',
            chief_complaint='Tooth pain'
        )
        
        # Create a tooth
        self.tooth = Tooth.objects.create(
            number=18,
            name='Upper Right Third Molar',
            quadrant=1,
            position=8
        )
        
        # Create a condition
        self.condition = ToothCondition.objects.create(
            name='Deep Cavity',
            description='Deep dental decay'
        )
        
        # Create multiple appointments on different dates
        today = date.today()
        
        # First appointment (day 1)
        self.appointment1 = Appointment.objects.create(
            patient=self.patient,
            dentist=self.dentist,
            date=today,
            start_time=time(9, 0),
            end_time=time(9, 30),
            status='scheduled'
        )
        
        # Second appointment (day 2)
        self.appointment2 = Appointment.objects.create(
            patient=self.patient,
            dentist=self.dentist,
            date=today + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(10, 30),
            status='scheduled'
        )
        
        # Third appointment (day 3)
        self.appointment3 = Appointment.objects.create(
            patient=self.patient,
            dentist=self.dentist,
            date=today + timedelta(days=2),
            start_time=time(11, 0),
            end_time=time(11, 30),
            status='scheduled'
        )
        
        # Login
        self.client.login(username=self.dentist.username, password='dentistpassword')
    
    def test_treatment_history_across_appointments(self):
        """Test that treatment history correctly tracks changes across different appointments"""
        
        # Step 1: Create a treatment during the first appointment
        treatment_data = {
            'tooth_ids': str(self.tooth.id),
            'condition': self.condition.id,
            'appointment': self.appointment1.id,
            'description': 'Initial cavity assessment',
            'status': 'planned',
            'cost': '200.00'
        }
        
        response = self.client.post(
            reverse('add_treatment', kwargs={'patient_id': self.patient.id}),
            treatment_data
        )
        
        # Check that a treatment was created
        self.assertEqual(Treatment.objects.count(), 1)
        treatment = Treatment.objects.first()
        
        # Check that initial history was created
        self.assertEqual(TreatmentHistory.objects.count(), 1)
        history1 = TreatmentHistory.objects.first()
        self.assertEqual(history1.treatment, treatment)
        self.assertIsNone(history1.previous_status)
        self.assertEqual(history1.new_status, 'planned')
        self.assertEqual(history1.appointment, self.appointment1)
        
        # Step 2: Update the treatment during the second appointment
        update_data = {
            'status': 'in_progress',
            'description': 'Started cavity treatment',
            'cost': '200.00',
            'current_appointment': self.appointment2.id,
            'referer': reverse('appointment_detail', kwargs={'pk': self.appointment2.id})
        }
        
        response = self.client.post(
            reverse('treatment_update', kwargs={'pk': treatment.pk}),
            update_data
        )
        
        # Refresh the treatment from the database
        treatment.refresh_from_db()
        
        # Check that the treatment was updated
        self.assertEqual(treatment.status, 'in_progress')
        self.assertEqual(treatment.description, 'Started cavity treatment')
        
        # Check that the treatment is now associated with the second appointment
        self.assertEqual(treatment.appointment, self.appointment2)
        
        # Check that a new history entry was created
        self.assertEqual(TreatmentHistory.objects.count(), 2)
        history2 = TreatmentHistory.objects.latest('created_at')
        self.assertEqual(history2.treatment, treatment)
        self.assertEqual(history2.previous_status, 'planned')
        self.assertEqual(history2.new_status, 'in_progress')
        self.assertEqual(history2.appointment, self.appointment2)
        
        # Step 3: Complete the treatment during the third appointment
        update_data = {
            'status': 'completed',
            'description': 'Cavity treatment completed',
            'cost': '200.00',
            'current_appointment': self.appointment3.id,
            'referer': reverse('appointment_detail', kwargs={'pk': self.appointment3.id})
        }
        
        response = self.client.post(
            reverse('treatment_update', kwargs={'pk': treatment.pk}),
            update_data
        )
        
        # Refresh the treatment from the database
        treatment.refresh_from_db()
        
        # Check that the treatment was updated
        self.assertEqual(treatment.status, 'completed')
        self.assertEqual(treatment.description, 'Cavity treatment completed')
        
        # Check that the treatment is now associated with the third appointment
        self.assertEqual(treatment.appointment, self.appointment3)
        
        # Check that a new history entry was created
        self.assertEqual(TreatmentHistory.objects.count(), 3)
        history3 = TreatmentHistory.objects.latest('created_at')
        self.assertEqual(history3.treatment, treatment)
        self.assertEqual(history3.previous_status, 'in_progress')
        self.assertEqual(history3.new_status, 'completed')
        self.assertEqual(history3.appointment, self.appointment3)
        
        # Step 4: View the treatment detail page to check history display
        response = self.client.get(reverse('treatment_detail', kwargs={'pk': treatment.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Check that all history entries are in the context
        treatment_history = response.context['treatment_history']
        self.assertEqual(len(treatment_history), 3)
        
        # Check that the history entries are in reverse chronological order (newest first)
        self.assertEqual(treatment_history[0], history3)
        self.assertEqual(treatment_history[1], history2)
        self.assertEqual(treatment_history[2], history1)
        
        # Step 5: Check the API endpoint for tooth treatments
        response = self.client.get(
            reverse('get_tooth_treatments', kwargs={'tooth_id': self.tooth.number}) + 
            f'?patient_id={self.patient.id}'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the treatment history is included in the API response
        self.assertEqual(len(data['treatments']), 1)
        self.assertEqual(len(data['treatments'][0]['history']), 3)
        
        # Check that each history entry includes the appointment date
        for history_entry in data['treatments'][0]['history']:
            self.assertIsNotNone(history_entry['appointment_date'])
            self.assertIsNotNone(history_entry['appointment_id']) 