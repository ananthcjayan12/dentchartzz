from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Patient, Payment, PaymentItem
from decimal import Decimal
from datetime import date

class BalancePaymentTest(TestCase):
    """Tests specifically for the balance payment functionality"""
    
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
    
    def test_balance_calculation_with_multiple_payments(self):
        """Test balance calculation with multiple payments including balance payments"""
        # Create first payment (regular)
        payment1 = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('2000.00'),
            amount_paid=Decimal('1000.00'),
            payment_method='cash',
            created_by=self.user
        )
        
        # Create payment item
        PaymentItem.objects.create(
            payment=payment1,
            description='Initial treatment',
            amount=Decimal('2000.00')
        )
        
        # Create second payment (regular)
        payment2 = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('1000.00'),
            amount_paid=Decimal('500.00'),
            payment_method='card',
            created_by=self.user
        )
        
        # Create payment item
        PaymentItem.objects.create(
            payment=payment2,
            description='Additional treatment',
            amount=Decimal('1000.00')
        )
        
        # Create third payment (balance payment)
        payment3 = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('0.00'),
            amount_paid=Decimal('800.00'),
            payment_method='cash',
            created_by=self.user
        )
        
        # Create payment item
        PaymentItem.objects.create(
            payment=payment3,
            description='Payment towards outstanding balance',
            amount=Decimal('800.00')
        )
        
        # Check the balance calculation
        url = reverse('get_patient_balance', args=[self.patient.id])
        response = self.client.get(url)
        data = response.json()
        
        # Total treatment cost should be 2000 + 1000 + 0 = 3000
        self.assertEqual(data['total_treatment_cost'], 3000.0)
        
        # Total paid should be 1000 + 500 + 800 = 2300
        self.assertEqual(data['total_paid'], 2300.0)
        
        # Balance due should be 3000 - 2300 = 700
        self.assertEqual(data['balance_due'], 700.0)
    
    def test_balance_payment_with_zero_total_amount(self):
        """Test that balance payments have a total_amount of 0"""
        # Create a regular payment first to create a balance
        Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('1000.00'),
            amount_paid=Decimal('500.00'),
            payment_method='cash',
            created_by=self.user
        )
        
        # Create a balance payment directly
        balance_payment = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('0.00'),
            amount_paid=Decimal('300.00'),
            payment_method='card',
            created_by=self.user,
            notes='Balance payment'
        )
        
        # Create a payment item for the balance payment
        PaymentItem.objects.create(
            payment=balance_payment,
            description='Payment towards outstanding balance',
            amount=Decimal('300.00')
        )
        
        # Check payment details
        self.assertEqual(balance_payment.total_amount, Decimal('0.00'))
        self.assertEqual(balance_payment.amount_paid, Decimal('300.00'))
        self.assertTrue(balance_payment.is_balance_payment)
    
    def test_is_balance_payment_property(self):
        """Test the is_balance_payment property of the Payment model"""
        # Create a regular payment
        regular_payment = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('1000.00'),
            amount_paid=Decimal('500.00'),
            payment_method='cash',
            created_by=self.user
        )
        
        # Create a balance payment
        balance_payment = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('0.00'),
            amount_paid=Decimal('300.00'),
            payment_method='card',
            created_by=self.user
        )
        
        # Check the is_balance_payment property
        self.assertFalse(regular_payment.is_balance_payment)
        self.assertTrue(balance_payment.is_balance_payment)
    
    def test_balance_payment_display_in_templates(self):
        """Test that balance payments are displayed correctly in templates"""
        # Create a regular payment
        regular_payment = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('1000.00'),
            amount_paid=Decimal('500.00'),
            payment_method='cash',
            created_by=self.user
        )
        
        # Create a payment item
        PaymentItem.objects.create(
            payment=regular_payment,
            description='Regular payment',
            amount=Decimal('1000.00')
        )
        
        # Create a balance payment
        balance_payment = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('0.00'),
            amount_paid=Decimal('300.00'),
            payment_method='card',
            created_by=self.user
        )
        
        # Create a payment item
        PaymentItem.objects.create(
            payment=balance_payment,
            description='Payment towards outstanding balance',
            amount=Decimal('300.00')
        )
        
        # Check the payment list template
        url = reverse('payment_list', args=[self.patient.id])
        response = self.client.get(url)
        
        # Check that the balance payment is displayed correctly
        self.assertContains(response, 'Balance Payment')  # Text for balance payment
        self.assertContains(response, 'Paid towards balance')  # Text for balance payment
        
        # Check the payment detail template for the balance payment
        url = reverse('payment_detail', args=[balance_payment.id])
        response = self.client.get(url)
        
        # Check that the balance payment is displayed correctly
        self.assertContains(response, 'Balance Payment')  # Text for balance payment
        self.assertContains(response, 'Paid towards balance')  # Text for balance payment
    
    def test_full_payment_workflow(self):
        """Test a complete payment workflow with regular and balance payments"""
        # 1. Create a regular payment for a treatment
        url = reverse('payment_create', args=[self.patient.id])
        
        data = {
            'payment_date': date.today().strftime('%Y-%m-%d'),
            'payment_method': 'cash',
            'total_amount': '2000.00',
            'amount_paid': '1000.00',  # Partial payment
            'notes': 'Initial payment',
            
            # Formset data for payment items
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-description': 'Dental treatment',
            'items-0-amount': '2000.00',
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Check that the payment was created
        self.assertEqual(Payment.objects.count(), 1)
        
        # 2. Create another regular payment for a different treatment
        data = {
            'payment_date': date.today().strftime('%Y-%m-%d'),
            'payment_method': 'card',
            'total_amount': '1000.00',
            'amount_paid': '500.00',  # Partial payment
            'notes': 'Second payment',
            
            # Formset data for payment items
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-description': 'Additional treatment',
            'items-0-amount': '1000.00',
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Check that the payment was created
        self.assertEqual(Payment.objects.count(), 2)
        
        # 3. Check the balance
        url = reverse('get_patient_balance', args=[self.patient.id])
        response = self.client.get(url)
        data = response.json()
        
        # Total treatment cost should be 2000 + 1000 = 3000
        self.assertEqual(data['total_treatment_cost'], 3000.0)
        
        # Total paid should be 1000 + 500 = 1500
        self.assertEqual(data['total_paid'], 1500.0)
        
        # Balance due should be 3000 - 1500 = 1500
        self.assertEqual(data['balance_due'], 1500.0)
        
        # 4. Make a balance payment
        url = reverse('payment_balance', args=[self.patient.id])
        
        data = {
            'is_balance_payment': 'true',
            'payment_date': date.today().strftime('%Y-%m-%d'),
            'payment_method': 'cash',
            'total_amount': '0.00',
            'amount_paid': '1000.00',  # Partial balance payment
            'notes': 'Balance payment',
            
            # Formset data for payment items
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-description': 'Payment towards outstanding balance',
            'items-0-amount': '1000.00',
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Check that the payment was created
        self.assertEqual(Payment.objects.count(), 3)
        
        # 5. Check the balance again
        url = reverse('get_patient_balance', args=[self.patient.id])
        response = self.client.get(url)
        data = response.json()
        
        # Total treatment cost should still be 3000
        self.assertEqual(data['total_treatment_cost'], 3000.0)
        
        # Total paid should be 1000 + 500 + 1000 = 2500
        self.assertEqual(data['total_paid'], 2500.0)
        
        # Balance due should be 3000 - 2500 = 500
        self.assertEqual(data['balance_due'], 500.0)
        
        # 6. Make a final balance payment
        url = reverse('payment_balance', args=[self.patient.id])
        
        data = {
            'is_balance_payment': 'true',
            'payment_date': date.today().strftime('%Y-%m-%d'),
            'payment_method': 'card',
            'total_amount': '0.00',
            'amount_paid': '500.00',  # Final payment
            'notes': 'Final payment',
            
            # Formset data for payment items
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-description': 'Final payment towards outstanding balance',
            'items-0-amount': '500.00',
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Check that the payment was created
        self.assertEqual(Payment.objects.count(), 4)
        
        # 7. Check the final balance
        url = reverse('get_patient_balance', args=[self.patient.id])
        response = self.client.get(url)
        data = response.json()
        
        # Total treatment cost should still be 3000
        self.assertEqual(data['total_treatment_cost'], 3000.0)
        
        # Total paid should be 1000 + 500 + 1000 + 500 = 3000
        self.assertEqual(data['total_paid'], 3000.0)
        
        # Balance due should be 3000 - 3000 = 0
        self.assertEqual(data['balance_due'], 0.0)
        
        # 8. Check that the "Pay Balance" button is not displayed anymore
        url = reverse('patient_detail', args=[self.patient.id])
        response = self.client.get(url)
        
        # Since the balance is fully paid, the "Pay Balance" button should not be displayed
        self.assertNotContains(response, 'Pay Balance') 