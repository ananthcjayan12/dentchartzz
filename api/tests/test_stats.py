from decimal import Decimal
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from api.models import Clinic, Patient, Appointment, Payment, ClinicMembership
from django.contrib.auth.models import User

class ClinicStatsTests(APITestCase):
    def setUp(self):
        # Create test clinic and user
        self.clinic = Clinic.objects.create(name="Test Clinic")
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create clinic membership
        self.membership = ClinicMembership.objects.create(
            user=self.user,
            clinic=self.clinic,
            role='dentist'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self.create_test_data()
    
    def create_test_data(self):
        # Create patients
        for i in range(5):
            Patient.objects.create(
                name=f"Patient {i}",
                clinic=self.clinic,
                age=30,
                gender='M'
            )
        
        # Create appointments
        today = timezone.now().date()
        for i in range(3):
            Appointment.objects.create(
                clinic=self.clinic,
                patient=Patient.objects.first(),
                dentist=self.user,
                date=today,
                start_time='09:00',
                end_time='10:00',
                status='scheduled'
            )
    
    def test_patient_stats(self):
        url = reverse('clinic-patient-stats', kwargs={'clinic_id': self.clinic.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['totalPatients'], 5)
        self.assertIn('monthlyGrowth', response.data)
        self.assertIn('newPatientsThisMonth', response.data)
        self.assertIn('activePatients', response.data)
    
    def test_appointment_stats(self):
        url = reverse('clinic-appointment-stats', kwargs={'clinic_id': self.clinic.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['todayCount'], 3)
        self.assertIn('dailyChange', response.data)
        self.assertIn('monthlyRevenue', response.data)
        self.assertIn('completionRate', response.data) 