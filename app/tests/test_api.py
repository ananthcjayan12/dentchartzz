from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import UserProfile, Patient, Appointment
from datetime import date, time, datetime, timedelta
import json
import uuid


class PatientComplaintsAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create a user with unique username
        username = f"testuser_{uuid.uuid4().hex[:8]}"
        self.user = User.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password='testpassword'
        )
        
        # Get the profile that was automatically created by the signal
        self.profile = UserProfile.objects.get(user=self.user)
        
        # Update the profile
        self.profile.role = 'staff'
        self.profile.save()
        
        # Create a patient with chief complaint
        self.patient = Patient.objects.create(
            name='Test Patient',
            age=30,
            gender='M',
            phone='1234567890',
            address='123 Test Street',
            chief_complaint='Toothache in upper right molar'
        )
        
        # Create a patient without chief complaint
        self.patient_no_complaint = Patient.objects.create(
            name='No Complaint Patient',
            age=25,
            gender='F',
            phone='9876543210',
            address='456 Patient Avenue'
        )
        
        # Login
        self.client.login(username=self.user.username, password='testpassword')
    
    def test_get_patient_complaints_valid(self):
        """Test that patient complaints can be retrieved for a valid patient"""
        response = self.client.get(reverse('get_patient_complaints', kwargs={'patient_id': self.patient.id}))
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains the chief complaint
        self.assertIn('complaints', data)
        self.assertIn('Toothache in upper right molar', data['complaints'])
    
    def test_get_patient_complaints_no_complaint(self):
        """Test that empty complaint is returned for patient without complaint"""
        response = self.client.get(reverse('get_patient_complaints', kwargs={'patient_id': self.patient_no_complaint.id}))
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains an empty list of complaints
        self.assertIn('complaints', data)
        self.assertEqual(len(data['complaints']), 0)
    
    def test_get_patient_complaints_invalid_id(self):
        """Test that appropriate error is returned for invalid patient ID"""
        # Use a non-existent patient ID
        invalid_id = 9999
        
        response = self.client.get(reverse('get_patient_complaints', kwargs={'patient_id': invalid_id}))
        
        self.assertEqual(response.status_code, 404)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains an error message
        self.assertIn('error', data)
    
    def test_get_patient_complaints_unauthenticated(self):
        """Test that unauthenticated users cannot access the API"""
        # Logout
        self.client.logout()
        
        response = self.client.get(reverse('get_patient_complaints', kwargs={'patient_id': self.patient.id}))
        
        # Should redirect to login page
        self.assertNotEqual(response.status_code, 200)


class TimeSlotAPITest(TestCase):
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
        
        # Get the profile that was automatically created by the signal
        self.dentist_profile = UserProfile.objects.get(user=self.dentist)
        
        # Update the profile
        self.dentist_profile.role = 'dentist'
        self.dentist_profile.save()
        
        # Create another dentist with unique username
        dentist2_username = f"dentist2_{uuid.uuid4().hex[:8]}"
        self.dentist2 = User.objects.create_user(
            username=dentist2_username,
            email=f'{dentist2_username}@example.com',
            password='dentist2password',
            first_name='Doctor',
            last_name='Smith'
        )
        
        # Get the profile that was automatically created by the signal
        self.dentist2_profile = UserProfile.objects.get(user=self.dentist2)
        
        # Update the profile
        self.dentist2_profile.role = 'dentist'
        self.dentist2_profile.save()
        
        # Create a patient
        self.patient = Patient.objects.create(
            name='Test Patient',
            age=30,
            gender='M',
            phone='1234567890',
            address='123 Test Street'
        )
        
        # Create some appointments for the first dentist
        tomorrow = date.today() + timedelta(days=1)
        
        self.appointment1 = Appointment.objects.create(
            patient=self.patient,
            dentist=self.dentist,
            date=tomorrow,
            start_time=time(9, 0),  # 9:00 AM
            end_time=time(9, 30),   # 9:30 AM
            status='scheduled'
        )
        
        self.appointment2 = Appointment.objects.create(
            patient=self.patient,
            dentist=self.dentist,
            date=tomorrow,
            start_time=time(11, 0),  # 11:00 AM
            end_time=time(11, 30),   # 11:30 AM
            status='scheduled'
        )
        
        # Login
        self.client.login(username=self.dentist.username, password='dentistpassword')
    
    def test_get_time_slots_valid(self):
        """Test that available time slots can be retrieved for a valid date and dentist"""
        tomorrow = date.today() + timedelta(days=1)
        
        response = self.client.get(
            reverse('get_time_slots') + 
            f'?date={tomorrow.strftime("%Y-%m-%d")}&dentist={self.dentist.id}'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains time slots
        self.assertIn('time_slots', data)
        
        # The time slots should be a list of objects
        time_slots = data['time_slots']
        self.assertTrue(isinstance(time_slots, list))
        self.assertTrue(len(time_slots) > 0)
        
        # Check that each time slot has the expected structure
        for slot in time_slots:
            self.assertIn('time', slot)
            self.assertIn('display', slot)
            self.assertIn('available', slot)
            self.assertIn('selected', slot)
        
        # Check that booked slots are marked as unavailable
        booked_times = ['09:00', '11:00']  # Times of existing appointments
        for slot in time_slots:
            if slot['time'] in booked_times:
                self.assertFalse(slot['available'])
    
    def test_get_time_slots_different_dentist(self):
        """Test that time slots for a different dentist don't exclude appointments of the first dentist"""
        tomorrow = date.today() + timedelta(days=1)
        
        response = self.client.get(
            reverse('get_time_slots') + 
            f'?date={tomorrow.strftime("%Y-%m-%d")}&dentist={self.dentist2.id}'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains time slots
        self.assertIn('time_slots', data)
        
        # The time slots should be a list of objects
        time_slots = data['time_slots']
        self.assertTrue(isinstance(time_slots, list))
        self.assertTrue(len(time_slots) > 0)
        
        # Check that slots that are booked for the first dentist are available for the second dentist
        booked_times = ['09:00', '11:00']  # Times of existing appointments for first dentist
        for slot in time_slots:
            if slot['time'] in booked_times:
                self.assertTrue(slot['available'])
    
    def test_get_time_slots_missing_parameters(self):
        """Test that appropriate error is returned when parameters are missing"""
        # Missing date parameter
        response = self.client.get(
            reverse('get_time_slots') + 
            f'?dentist={self.dentist.id}'
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains an error message
        self.assertIn('error', data)
        
        # Missing dentist parameter
        tomorrow = date.today() + timedelta(days=1)
        response = self.client.get(
            reverse('get_time_slots') + 
            f'?date={tomorrow.strftime("%Y-%m-%d")}'
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains an error message
        self.assertIn('error', data)
    
    def test_get_time_slots_invalid_dentist(self):
        """Test that appropriate behavior for invalid dentist ID"""
        tomorrow = date.today() + timedelta(days=1)
        
        # Use a non-existent dentist ID
        invalid_id = 9999
        
        response = self.client.get(
            reverse('get_time_slots') + 
            f'?date={tomorrow.strftime("%Y-%m-%d")}&dentist={invalid_id}'
        )
        
        # The API should still return a 200 status code
        self.assertEqual(response.status_code, 200)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains time slots
        self.assertIn('time_slots', data)
        
        # The time slots should be a list of objects
        time_slots = data['time_slots']
        self.assertTrue(isinstance(time_slots, list))
        self.assertTrue(len(time_slots) > 0)
        
        # All slots should be available since there are no appointments for this dentist
        for slot in time_slots:
            self.assertTrue(slot['available'])
    
    def test_get_time_slots_invalid_date_format(self):
        """Test that appropriate error is returned for invalid date format"""
        response = self.client.get(
            reverse('get_time_slots') + 
            f'?date=invalid-date&dentist={self.dentist.id}'
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the response contains an error message
        self.assertIn('error', data) 