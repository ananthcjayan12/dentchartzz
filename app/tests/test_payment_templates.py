from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Patient, Payment, PaymentItem
from decimal import Decimal
from datetime import date

class PaymentTemplateTest(TestCase):
    """Tests for the payment templates"""
    
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
        
        # Create a regular payment
        self.regular_payment = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('1000.00'),
            amount_paid=Decimal('500.00'),
            payment_method='cash',
            created_by=self.user
        )
        
        # Create a payment item for the regular payment
        self.regular_payment_item = PaymentItem.objects.create(
            payment=self.regular_payment,
            description='Dental procedure',
            amount=Decimal('1000.00')
        )
        
        # Create a balance payment
        self.balance_payment = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('0.00'),
            amount_paid=Decimal('200.00'),
            payment_method='card',
            created_by=self.user
        )
        
        # Create a payment item for the balance payment
        self.balance_payment_item = PaymentItem.objects.create(
            payment=self.balance_payment,
            description='Payment towards outstanding balance',
            amount=Decimal('200.00')
        )
    
    def test_payment_card_template(self):
        """Test the payment card template"""
        url = reverse('patient_detail', args=[self.patient.id])
        response = self.client.get(url)
        
        # Check that the payment card is displayed correctly
        self.assertEqual(response.status_code, 200)
        
        # Check payment summary section
        self.assertContains(response, 'Total Amount Billed')
        self.assertContains(response, '$1000.00')  # Total amount
        self.assertContains(response, 'Total Paid')
        self.assertContains(response, '$700.00')   # Total paid (500 + 200)
        self.assertContains(response, 'Balance Due')
        self.assertContains(response, '$300.00')   # Balance due
        
        # Check recent payments table
        self.assertContains(response, 'Recent Payments')
        self.assertContains(response, 'Balance Payment')  # Text for balance payment
        self.assertContains(response, 'Paid towards balance')  # Text for balance payment
    
    def test_payment_list_template(self):
        """Test the payment list template"""
        url = reverse('payment_list', args=[self.patient.id])
        response = self.client.get(url)
        
        # Check that the payment list is displayed correctly
        self.assertEqual(response.status_code, 200)
        
        # Check payment summary section
        self.assertContains(response, 'Payment Summary')
        self.assertContains(response, '$1000.00')  # Total amount
        self.assertContains(response, '$700.00')   # Total paid
        self.assertContains(response, '$300.00')   # Balance due
        
        # Check payments table
        self.assertContains(response, 'All Payments')
        self.assertContains(response, 'Balance Payment')  # Text for balance payment
        self.assertContains(response, 'Paid towards balance')  # Text for balance payment
        
        # Check that the "Pay Balance" button is displayed (since there's a balance)
        self.assertContains(response, 'Pay Balance')
    
    def test_payment_detail_template_regular_payment(self):
        """Test the payment detail template for a regular payment"""
        url = reverse('payment_detail', args=[self.regular_payment.id])
        response = self.client.get(url)
        
        # Check that the payment detail is displayed correctly
        self.assertEqual(response.status_code, 200)
        
        # Check payment information section
        self.assertContains(response, 'Payment Information')
        self.assertContains(response, 'Payment Date')
        self.assertContains(response, 'Payment Method')
        self.assertContains(response, 'Cash')  # Payment method
        self.assertContains(response, 'Total Amount')
        self.assertContains(response, '$1000.00')  # Total amount
        self.assertContains(response, 'Amount Paid')
        self.assertContains(response, '$500.00')   # Amount paid
        self.assertContains(response, 'Balance')
        self.assertContains(response, '$500.00')   # Balance
        
        # Check payment items section
        self.assertContains(response, 'Payment Items')
        self.assertContains(response, 'Dental procedure')  # Item description
        self.assertContains(response, '$1000.00')  # Item amount
    
    def test_payment_detail_template_balance_payment(self):
        """Test the payment detail template for a balance payment"""
        url = reverse('payment_detail', args=[self.balance_payment.id])
        response = self.client.get(url)
        
        # Check that the payment detail is displayed correctly
        self.assertEqual(response.status_code, 200)
        
        # Check payment information section
        self.assertContains(response, 'Payment Information')
        self.assertContains(response, 'Payment Date')
        self.assertContains(response, 'Payment Method')
        self.assertContains(response, 'Credit/Debit Card')  # Payment method
        self.assertContains(response, 'Total Amount')
        self.assertContains(response, 'Balance Payment')  # Text for balance payment
        self.assertContains(response, 'Amount Paid')
        self.assertContains(response, '$200.00')   # Amount paid
        self.assertContains(response, 'Balance')
        self.assertContains(response, 'Paid towards balance')  # Text for balance payment
        
        # Check payment items section
        self.assertContains(response, 'Payment Items')
        self.assertContains(response, 'Payment towards outstanding balance')  # Item description
        self.assertContains(response, '$200.00')  # Item amount
    
    def test_payment_form_template_regular(self):
        """Test the payment form template for a regular payment"""
        url = reverse('payment_create', args=[self.patient.id])
        response = self.client.get(url)
        
        # Check that the payment form is displayed correctly
        self.assertEqual(response.status_code, 200)
        
        # Check form header
        self.assertContains(response, 'Add Payment')
        self.assertContains(response, 'Record a payment for Test Patient')
        
        # Check form fields
        self.assertContains(response, 'Payment Date')
        self.assertContains(response, 'Payment Method')
        self.assertContains(response, 'Total Amount')
        self.assertContains(response, 'Amount Paid')
        self.assertContains(response, 'Notes')
        
        # Check payment items formset
        self.assertContains(response, 'Payment Items')
        self.assertContains(response, 'Description')
        self.assertContains(response, 'Amount')
        self.assertContains(response, 'Treatment')
        
        # Check that the balance payment hidden field is not present
        self.assertNotContains(response, 'is_balance_payment')
    
    def test_payment_form_template_balance(self):
        """Test the payment form template for a balance payment"""
        url = reverse('payment_balance', args=[self.patient.id])
        response = self.client.get(url)
        
        # Check that the payment form is displayed correctly
        self.assertEqual(response.status_code, 200)
        
        # Check form header
        self.assertContains(response, 'Pay Outstanding Balance')
        self.assertContains(response, 'Record a payment towards Test Patient\'s outstanding balance')
        
        # Check form fields
        self.assertContains(response, 'Payment Date')
        self.assertContains(response, 'Payment Method')
        self.assertContains(response, 'Total Amount')
        self.assertContains(response, 'Amount Paid')
        self.assertContains(response, 'Notes')
        
        # Check payment items formset
        self.assertContains(response, 'Payment Items')
        self.assertContains(response, 'Description')
        self.assertContains(response, 'Amount')
        
        # Check that the balance payment hidden field is present
        self.assertContains(response, 'is_balance_payment')
        
        # Check that the amount paid is pre-filled with the balance due
        self.assertContains(response, '$300.00')  # Balance due
    
    def test_payment_form_submission_regular(self):
        """Test submitting the payment form for a regular payment"""
        url = reverse('payment_create', args=[self.patient.id])
        
        # Form data for a regular payment
        data = {
            'payment_date': date.today().strftime('%Y-%m-%d'),
            'payment_method': 'cash',
            'total_amount': '800.00',
            'amount_paid': '400.00',
            'notes': 'Test payment',
            
            # Formset data for payment items
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-description': 'Test item',
            'items-0-amount': '800.00',
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Check that the payment was created
        self.assertEqual(Payment.objects.count(), 3)
        payment = Payment.objects.latest('created_at')
        
        # Check payment details
        self.assertEqual(payment.patient, self.patient)
        self.assertEqual(payment.total_amount, Decimal('800.00'))
        self.assertEqual(payment.amount_paid, Decimal('400.00'))
        
        # Check that we were redirected to the patient detail page
        self.assertRedirects(response, reverse('patient_detail', args=[self.patient.id]))
        
        # Check that the success message is displayed
        self.assertContains(response, 'Payment recorded successfully')
    
    def test_payment_form_submission_balance(self):
        """Test submitting the payment form for a balance payment"""
        url = reverse('payment_balance', args=[self.patient.id])
        
        # Form data for a balance payment
        data = {
            'is_balance_payment': 'true',
            'payment_date': date.today().strftime('%Y-%m-%d'),
            'payment_method': 'card',
            'total_amount': '0.00',
            'amount_paid': '300.00',
            'notes': 'Balance payment',
            
            # Formset data for payment items
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-description': 'Payment towards outstanding balance',
            'items-0-amount': '300.00',
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Check that the payment was created
        self.assertEqual(Payment.objects.count(), 3)
        payment = Payment.objects.latest('created_at')
        
        # Check payment details
        self.assertEqual(payment.patient, self.patient)
        self.assertEqual(payment.total_amount, Decimal('0.00'))
        self.assertEqual(payment.amount_paid, Decimal('300.00'))
        
        # Check that we were redirected to the patient detail page
        self.assertRedirects(response, reverse('patient_detail', args=[self.patient.id]))
        
        # Check that the success message is displayed
        self.assertContains(response, 'Balance payment recorded successfully')
        
        # Check that the balance is now fully paid
        url = reverse('get_patient_balance', args=[self.patient.id])
        response = self.client.get(url)
        data = response.json()
        
        # Balance due should be 0
        self.assertEqual(data['balance_due'], 0.0) 