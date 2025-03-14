import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from datetime import date, timedelta
from decimal import Decimal
from api.models import Payment, PaymentItem, Treatment, Patient, Clinic, ClinicMembership, Appointment, Tooth, ToothCondition

@pytest.mark.django_db
class TestPaymentEndpoints:
    """Test payment endpoints."""
    
    @pytest.fixture
    def patient(self, clinic):
        """Create and return a test patient."""
        return Patient.objects.create(
            clinic=clinic,
            name='Test Patient',
            age=30,
            gender='M',
            phone='1234567890'
        )
    
    @pytest.fixture
    def dentist(self):
        """Create and return a dentist user."""
        return User.objects.create_user(
            username='dentist',
            email='dentist@example.com',
            password='dentistpassword',
            first_name='Test',
            last_name='Dentist'
        )
    
    @pytest.fixture
    def dentist_membership(self, dentist, clinic):
        """Create and return a clinic membership for the dentist."""
        return ClinicMembership.objects.create(
            user=dentist,
            clinic=clinic,
            role='dentist',
            is_primary=True
        )
    
    @pytest.fixture
    def appointment(self, clinic, patient, dentist):
        """Create and return a test appointment."""
        tomorrow = date.today() + timedelta(days=1)
        return Appointment.objects.create(
            clinic=clinic,
            patient=patient,
            dentist=dentist,
            date=tomorrow,
            start_time='10:00:00',
            end_time='10:30:00',
            status='scheduled',
            notes='Regular checkup'
        )
    
    @pytest.fixture
    def tooth(self):
        """Create and return a test tooth."""
        return Tooth.objects.create(
            number=11,
            name='Upper Right Central Incisor',
            quadrant=1,
            position=1
        )
    
    @pytest.fixture
    def tooth_condition(self, clinic):
        """Create and return a test tooth condition."""
        return ToothCondition.objects.create(
            clinic=clinic,
            name='Cavity',
            description='Dental caries'
        )
    
    @pytest.fixture
    def treatment(self, clinic, patient, tooth, tooth_condition, appointment):
        """Create and return a test treatment."""
        return Treatment.objects.create(
            clinic=clinic,
            patient=patient,
            tooth=tooth,
            condition=tooth_condition,
            appointment=appointment,
            description='Filling needed',
            status='planned',
            cost=100.00
        )
    
    @pytest.fixture
    def payment(self, clinic, patient, appointment, user):
        """Create and return a test payment."""
        return Payment.objects.create(
            clinic=clinic,
            patient=patient,
            appointment=appointment,
            created_by=user,
            payment_date=date.today(),
            total_amount=100.00,
            amount_paid=50.00,
            payment_method='cash',
            notes='Initial payment'
        )
    
    @pytest.fixture
    def payment_item(self, payment, treatment):
        """Create and return a test payment item."""
        return PaymentItem.objects.create(
            payment=payment,
            treatment=treatment,
            description='Filling',
            amount=100.00
        )
    
    def test_list_payments(self, authenticated_client, user, clinic, clinic_membership, patient, appointment, payment, payment_item):
        """Test listing payments."""
        # Create another payment
        Payment.objects.create(
            clinic=clinic,
            patient=patient,
            appointment=appointment,
            created_by=user,
            payment_date=date.today() - timedelta(days=7),
            total_amount=200.00,
            amount_paid=200.00,
            payment_method='card',
            notes='Full payment'
        )
        
        url = reverse('clinic-payment-list', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Test filtering by patient
        url = f"{reverse('clinic-payment-list', args=[clinic.id])}?patient_id={patient.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Test filtering by date range
        one_week_ago = (date.today() - timedelta(days=7)).strftime('%Y-%m-%d')
        url = f"{reverse('clinic-payment-list', args=[clinic.id])}?start_date={one_week_ago}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
        # Test filtering by payment method
        url = f"{reverse('clinic-payment-list', args=[clinic.id])}?payment_method=cash"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['payment_method'] == 'cash'
    
    def test_create_payment(self, authenticated_client, user, clinic, clinic_membership, patient, appointment, treatment):
        """Test creating a payment."""
        url = reverse('clinic-payment-list', args=[clinic.id])
        data = {
            'patient_id': patient.id,
            'appointment_id': appointment.id,
            'payment_date': date.today().strftime('%Y-%m-%d'),
            'total_amount': '150.00',
            'amount_paid': '100.00',
            'payment_method': 'card',
            'notes': 'New payment',
            'payment_items': [
                {
                    'description': 'Treatment payment',
                    'amount': '150.00',
                    'treatment_id': treatment.id
                }
            ]
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['patient']['id'] == patient.id
        assert response.data['appointment']['id'] == appointment.id
        assert response.data['payment_date'] == date.today().strftime('%Y-%m-%d')
        assert float(response.data['total_amount']) == 150.00
        assert float(response.data['amount_paid']) == 100.00
        assert response.data['payment_method'] == 'card'
        assert response.data['notes'] == 'New payment'
        assert float(response.data['balance']) == 50.00
        assert len(response.data['items']) == 1
        assert response.data['items'][0]['description'] == 'Treatment payment'
        assert float(response.data['items'][0]['amount']) == 150.00
        
        # Verify the payment was created in the database
        payment = Payment.objects.get(notes='New payment')
        assert payment.clinic == clinic
        assert payment.patient == patient
        assert payment.appointment == appointment
        assert payment.created_by == user
        assert payment.total_amount == Decimal('150.00')
        assert payment.amount_paid == Decimal('100.00')
        
        # Verify the payment item was created
        payment_item = payment.items.first()
        assert payment_item is not None
        assert payment_item.description == 'Treatment payment'
        assert payment_item.amount == Decimal('150.00')
        assert payment_item.treatment == treatment
    
    def test_get_payment_detail(self, authenticated_client, user, clinic, clinic_membership, payment, payment_item):
        """Test getting payment details."""
        url = reverse('clinic-payment-detail', args=[clinic.id, payment.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == payment.id
        assert response.data['patient']['name'] == 'Test Patient'
        assert response.data['payment_date'] == date.today().strftime('%Y-%m-%d')
        assert float(response.data['total_amount']) == 100.00
        assert float(response.data['amount_paid']) == 50.00
        assert response.data['payment_method'] == 'cash'
        assert response.data['notes'] == 'Initial payment'
        assert float(response.data['balance']) == 50.00
        assert len(response.data['items']) == 1
        assert response.data['items'][0]['description'] == 'Filling'
        assert float(response.data['items'][0]['amount']) == 100.00
    
    def test_update_payment(self, authenticated_client, user, clinic, clinic_membership, payment, payment_item):
        """Test updating a payment."""
        url = reverse('clinic-payment-detail', args=[clinic.id, payment.id])
        data = {
            'amount_paid': '75.00',
            'notes': 'Updated payment'
        }
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert float(response.data['amount_paid']) == 75.00
        assert response.data['notes'] == 'Updated payment'
        assert float(response.data['balance']) == 25.00
        
        # Verify the payment was updated in the database
        payment.refresh_from_db()
        assert payment.amount_paid == Decimal('75.00')
        assert payment.notes == 'Updated payment'
    
    def test_update_payment_with_items(self, authenticated_client, user, clinic, clinic_membership, payment, payment_item, treatment):
        """Test updating a payment with new items."""
        url = reverse('clinic-payment-detail', args=[clinic.id, payment.id])
        data = {
            'payment_items': [
                {
                    'description': 'Updated item',
                    'amount': '120.00',
                    'treatment_id': treatment.id
                }
            ]
        }
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['items']) == 1
        assert response.data['items'][0]['description'] == 'Updated item'
        assert float(response.data['items'][0]['amount']) == 120.00
        
        # Verify the payment item was updated in the database
        payment.refresh_from_db()
        assert payment.items.count() == 1
        assert payment.items.first().description == 'Updated item'
        assert payment.items.first().amount == Decimal('120.00')
    
    def test_get_patient_balance(self, authenticated_client, user, clinic, clinic_membership, patient, payment, payment_item):
        """Test getting patient balance."""
        # Create another payment for the same patient
        Payment.objects.create(
            clinic=clinic,
            patient=patient,
            created_by=user,
            payment_date=date.today() - timedelta(days=7),
            total_amount=200.00,
            amount_paid=150.00,
            payment_method='card',
            notes='Another payment'
        )
        
        url = f"{reverse('clinic-payment-patient-balance', args=[clinic.id])}?patient_id={patient.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['patient_id'] == str(patient.id)
        assert float(response.data['total_amount']) == 300.00
        assert float(response.data['total_paid']) == 200.00
        assert float(response.data['balance']) == 100.00
        
        # Test without patient_id
        url = reverse('clinic-payment-patient-balance', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_patient_payments(self, authenticated_client, user, clinic, clinic_membership, patient, payment, payment_item):
        """Test getting patient payments."""
        # Create another payment for the same patient
        Payment.objects.create(
            clinic=clinic,
            patient=patient,
            created_by=user,
            payment_date=date.today() - timedelta(days=7),
            total_amount=200.00,
            amount_paid=150.00,
            payment_method='card',
            notes='Another payment'
        )
        
        # Create a payment for a different patient
        other_patient = Patient.objects.create(
            clinic=clinic,
            name='Other Patient',
            age=40,
            gender='F',
            phone='9876543210'
        )
        Payment.objects.create(
            clinic=clinic,
            patient=other_patient,
            created_by=user,
            payment_date=date.today(),
            total_amount=300.00,
            amount_paid=300.00,
            payment_method='cash',
            notes='Other patient payment'
        )
        
        url = f"{reverse('clinic-payment-patient-payments', args=[clinic.id])}?patient_id={patient.id}"
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        assert all(payment['patient'] == patient.id for payment in response.data)
        
        # Test without patient_id
        url = reverse('clinic-payment-patient-payments', args=[clinic.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_payment_from_different_clinic(self, authenticated_client, user, clinic, clinic_membership, patient):
        """Test that a user cannot access payments from a different clinic."""
        # Create another clinic
        other_clinic = Clinic.objects.create(
            name='Other Clinic',
            address='Other Address',
            phone='9999999999',
            email='other@example.com'
        )
        
        # Create a patient in the other clinic
        other_patient = Patient.objects.create(
            clinic=other_clinic,
            name='Other Patient',
            age=50,
            gender='M',
            phone='8888888888'
        )
        
        # Create a payment in the other clinic
        other_payment = Payment.objects.create(
            clinic=other_clinic,
            patient=other_patient,
            created_by=user,
            payment_date=date.today(),
            total_amount=100.00,
            amount_paid=100.00,
            payment_method='cash',
            notes='Other clinic payment'
        )
        
        # Try to access the payment from the other clinic
        url = reverse('clinic-payment-detail', args=[clinic.id, other_payment.id])
        response = authenticated_client.get(url)
        
        # Should return 404 because the payment doesn't exist in this clinic
        assert response.status_code == status.HTTP_404_NOT_FOUND 