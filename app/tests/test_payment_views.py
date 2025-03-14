from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Patient, Payment, PaymentItem, Treatment, ToothCondition, Tooth, Appointment
from decimal import Decimal
from datetime import date, time

class PaymentViewsDetailedTest(TestCase):
    """Detailed tests for the payment views"""
    
    def setUp(self):
        # Create a client
        self.client = Client()
        
        # Create a user and log in
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        self.client.login(username='testuser', password='testpassword')
        
        # Create a patient
        self.patient = Patient.objects.create(
            name='Test Patient',
            age=30,
            gender='M',
            phone='1234567890',
            address='123 Test St'
        )
        
        # Create an appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            dentist=self.user,
            date=date.today(),
            start_time=time(9, 0),
            end_time=time(10, 0),
            status='scheduled'
        )
        
        # Create a tooth and condition for treatments
        self.tooth = Tooth.objects.create(
            number=11,
            name='Upper Right Central Incisor',
            quadrant=1,
            position=1
        )
        
        self.condition = ToothCondition.objects.create(
            name='Cavity',
            description='Dental cavity'
        )
        
        # Create treatments
        self.treatment1 = Treatment.objects.create(
            patient=self.patient,
            tooth=self.tooth,
            condition=self.condition,
            description='Filling',
            status='completed',
            cost=Decimal('500.00'),
            appointment=self.appointment
        )
        
        self.treatment2 = Treatment.objects.create(
            patient=self.patient,
            tooth=self.tooth,
            condition=self.condition,
            description='Root Canal',
            status='planned',
            cost=Decimal('1000.00')
        )
    
    def test_payment_create_from_appointment(self):
        """Test creating a payment from an appointment"""
        url = reverse('payment_create_from_appointment', args=[self.patient.id, self.appointment.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/payment_form.html')
        self.assertContains(response, 'Add Payment')
        self.assertContains(response, self.patient.name)
        self.assertContains(response, self.appointment.date.strftime('%B %d, %Y'))
    
    def test_payment_create_post(self):
        """Test creating a payment via POST request"""
        url = reverse('payment_create', args=[self.patient.id])
        
        # Form data for a payment
        data = {
            'payment_date': date.today().strftime('%Y-%m-%d'),
            'payment_method': 'cash',
            'total_amount': '1500.00',
            'amount_paid': '1000.00',
            'notes': 'Test payment',
            
            # Formset data for payment items
            'items-TOTAL_FORMS': '2',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-description': 'Filling',
            'items-0-amount': '500.00',
            'items-0-treatment': self.treatment1.id,
            'items-1-description': 'Root Canal',
            'items-1-amount': '1000.00',
            'items-1-treatment': self.treatment2.id,
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Check that the payment was created
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        
        # Check payment details
        self.assertEqual(payment.patient, self.patient)
        self.assertEqual(payment.total_amount, Decimal('1500.00'))
        self.assertEqual(payment.amount_paid, Decimal('1000.00'))
        
        # Check payment items
        self.assertEqual(payment.items.count(), 2)
        items = payment.items.all()
        self.assertEqual(items[0].description, 'Filling')
        self.assertEqual(items[0].amount, Decimal('500.00'))
        self.assertEqual(items[0].treatment, self.treatment1)
        self.assertEqual(items[1].description, 'Root Canal')
        self.assertEqual(items[1].amount, Decimal('1000.00'))
        self.assertEqual(items[1].treatment, self.treatment2)
        
        # Check that we were redirected to the patient detail page
        self.assertRedirects(response, reverse('patient_detail', args=[self.patient.id]))
    
    def test_payment_balance_post(self):
        """Test creating a balance payment via POST request"""
        # First create a regular payment to create a balance
        payment = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('1500.00'),
            amount_paid=Decimal('1000.00'),
            payment_method='cash',
            created_by=self.user
        )
        
        # Create payment items
        PaymentItem.objects.create(
            payment=payment,
            description='Filling',
            amount=Decimal('500.00'),
            treatment=self.treatment1
        )
        
        PaymentItem.objects.create(
            payment=payment,
            description='Root Canal',
            amount=Decimal('1000.00'),
            treatment=self.treatment2
        )
        
        # Create a balance payment directly
        balance_payment = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('0.00'),
            amount_paid=Decimal('500.00'),
            payment_method='card',
            created_by=self.user,
            notes='Balance payment'
        )
        
        # Create a payment item for the balance payment
        PaymentItem.objects.create(
            payment=balance_payment,
            description='Payment towards outstanding balance',
            amount=Decimal('500.00')
        )
        
        # Check payment details
        self.assertEqual(balance_payment.patient, self.patient)
        self.assertEqual(balance_payment.total_amount, Decimal('0.00'))
        self.assertEqual(balance_payment.amount_paid, Decimal('500.00'))
        self.assertEqual(balance_payment.payment_method, 'card')
        self.assertTrue(balance_payment.is_balance_payment)
        
        # Check the balance calculation
        url = reverse('get_patient_balance', args=[self.patient.id])
        response = self.client.get(url)
        data = response.json()
        
        # Total treatment cost should be 1500
        self.assertEqual(data['total_treatment_cost'], 1500.0)
        
        # Total paid should be 1000 (regular) + 500 (balance) = 1500
        self.assertEqual(data['total_paid'], 1500.0)
        
        # Balance due should be 1500 - 1500 = 0
        self.assertEqual(data['balance_due'], 0.0)
    
    def test_payment_card_in_patient_detail(self):
        """Test that the payment card is displayed in the patient detail page"""
        # Create a payment
        payment = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('1500.00'),
            amount_paid=Decimal('1000.00'),
            payment_method='cash',
            created_by=self.user
        )
        
        # Create payment items
        PaymentItem.objects.create(
            payment=payment,
            description='Filling',
            amount=Decimal('500.00'),
            treatment=self.treatment1
        )
        
        PaymentItem.objects.create(
            payment=payment,
            description='Root Canal',
            amount=Decimal('1000.00'),
            treatment=self.treatment2
        )
        
        # Visit the patient detail page
        url = reverse('patient_detail', args=[self.patient.id])
        response = self.client.get(url)
        
        # Check that the payment card is displayed
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment Information')
        self.assertContains(response, '$1500.00')  # Total amount
        self.assertContains(response, '$1000.00')  # Amount paid
        self.assertContains(response, '$500.00')   # Balance due
        
        # Check that the "Pay Balance" button is displayed
        self.assertContains(response, 'Pay Balance')
    
    def test_payment_card_in_appointment_detail(self):
        """Test that the payment card is displayed in the appointment detail page"""
        # Create a payment linked to the appointment
        payment = Payment.objects.create(
            patient=self.patient,
            appointment=self.appointment,
            payment_date=date.today(),
            total_amount=Decimal('500.00'),
            amount_paid=Decimal('500.00'),
            payment_method='cash',
            created_by=self.user
        )
        
        # Create payment item
        PaymentItem.objects.create(
            payment=payment,
            description='Filling',
            amount=Decimal('500.00'),
            treatment=self.treatment1
        )
        
        # Visit the appointment detail page
        url = reverse('appointment_detail', args=[self.appointment.id])
        response = self.client.get(url)
        
        # Check that the payment card is displayed
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment Information')
        self.assertContains(response, '$500.00')  # Total amount and amount paid
        
        # Since the payment is fully paid, the "Pay Balance" button should not be displayed
        self.assertNotContains(response, 'Pay Balance')
    
    def test_multiple_payments_balance_calculation(self):
        """Test balance calculation with multiple payments"""
        # Create first payment (partial)
        payment1 = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('1500.00'),
            amount_paid=Decimal('500.00'),
            payment_method='cash',
            created_by=self.user
        )
        
        # Create payment items
        PaymentItem.objects.create(
            payment=payment1,
            description='Filling and Root Canal',
            amount=Decimal('1500.00')
        )
        
        # Create second payment (partial)
        payment2 = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('0.00'),
            amount_paid=Decimal('500.00'),
            payment_method='card',
            created_by=self.user
        )
        
        # Create payment item
        PaymentItem.objects.create(
            payment=payment2,
            description='Payment towards outstanding balance',
            amount=Decimal('500.00')
        )
        
        # Create third payment (final)
        payment3 = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('0.00'),
            amount_paid=Decimal('500.00'),
            payment_method='cash',
            created_by=self.user
        )
        
        # Create payment item
        PaymentItem.objects.create(
            payment=payment3,
            description='Final payment',
            amount=Decimal('500.00')
        )
        
        # Check the balance calculation
        url = reverse('get_patient_balance', args=[self.patient.id])
        response = self.client.get(url)
        data = response.json()
        
        # Total treatment cost should be 1500
        self.assertEqual(data['total_treatment_cost'], 1500.0)
        
        # Total paid should be 500 + 500 + 500 = 1500
        self.assertEqual(data['total_paid'], 1500.0)
        
        # Balance due should be 1500 - 1500 = 0
        self.assertEqual(data['balance_due'], 0.0)
        
        # Visit the payment list page
        url = reverse('payment_list', args=[self.patient.id])
        response = self.client.get(url)
        
        # Check that all payments are displayed
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment History')
        self.assertContains(response, '$1500.00')  # Total amount of first payment
        self.assertContains(response, 'Balance Payment')  # Text for balance payments
        
        # Since the balance is fully paid, the "Pay Balance" button should not be displayed
        self.assertNotContains(response, 'Pay Balance') 