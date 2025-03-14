from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from app.models import Patient, Payment, PaymentItem, Treatment, ToothCondition, Tooth
from decimal import Decimal
from datetime import date

class PaymentModelTest(TestCase):
    """Tests for the Payment model"""
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        
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
        
        # Create a balance payment
        self.balance_payment = Payment.objects.create(
            patient=self.patient,
            payment_date=date.today(),
            total_amount=Decimal('0.00'),
            amount_paid=Decimal('200.00'),
            payment_method='card',
            created_by=self.user
        )
    
    def test_payment_creation(self):
        """Test that payments are created correctly"""
        self.assertEqual(Payment.objects.count(), 2)
        self.assertEqual(self.regular_payment.patient, self.patient)
        self.assertEqual(self.regular_payment.total_amount, Decimal('1000.00'))
        self.assertEqual(self.regular_payment.amount_paid, Decimal('500.00'))
    
    def test_payment_balance_property(self):
        """Test the balance property of a payment"""
        self.assertEqual(self.regular_payment.balance, Decimal('500.00'))
        self.assertEqual(self.balance_payment.balance, Decimal('-200.00'))
    
    def test_is_balance_payment_property(self):
        """Test the is_balance_payment property"""
        self.assertFalse(self.regular_payment.is_balance_payment)
        self.assertTrue(self.balance_payment.is_balance_payment)
    
    def test_payment_string_representation(self):
        """Test the string representation of a payment"""
        expected = f"Payment #{self.regular_payment.id} - {self.patient.name} - {date.today()}"
        self.assertEqual(str(self.regular_payment), expected)


class PaymentViewsTest(TestCase):
    """Tests for the payment views"""
    
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
        
        # Create a treatment
        self.treatment = Treatment.objects.create(
            patient=self.patient,
            tooth=self.tooth,
            condition=self.condition,
            description='Filling',
            status='planned',
            cost=Decimal('500.00')
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
        
        # Create a payment item
        self.payment_item = PaymentItem.objects.create(
            payment=self.regular_payment,
            description='Dental filling',
            amount=Decimal('500.00'),
            treatment=self.treatment
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
    
    def test_payment_list_view(self):
        """Test the payment list view"""
        url = reverse('payment_list', args=[self.patient.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/payment_list.html')
        self.assertContains(response, 'Payment History')
        self.assertContains(response, '$1000.00')  # Total amount of regular payment
        self.assertContains(response, '$500.00')   # Amount paid of regular payment
        self.assertContains(response, 'Balance Payment')  # Text for balance payment
    
    def test_payment_detail_view(self):
        """Test the payment detail view"""
        url = reverse('payment_detail', args=[self.regular_payment.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/payment_detail.html')
        self.assertContains(response, 'Payment Details')
        self.assertContains(response, '$1000.00')  # Total amount
        self.assertContains(response, '$500.00')   # Amount paid
        self.assertContains(response, 'Dental filling')  # Payment item description
    
    def test_payment_create_view_get(self):
        """Test the payment create view (GET)"""
        url = reverse('payment_create', args=[self.patient.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/payment_form.html')
        self.assertContains(response, 'Add Payment')
        self.assertContains(response, self.patient.name)
    
    def test_payment_balance_view_get(self):
        """Test the payment balance view (GET)"""
        url = reverse('payment_balance', args=[self.patient.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'app/payment_form.html')
        self.assertContains(response, 'Pay Outstanding Balance')
        self.assertContains(response, self.patient.name)
        self.assertContains(response, 'is_balance_payment')
    
    def test_get_patient_balance_api(self):
        """Test the get_patient_balance API endpoint"""
        url = reverse('get_patient_balance', args=[self.patient.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Total amount should be 1000 (regular) + 0 (balance) = 1000
        self.assertEqual(data['total_treatment_cost'], 1000.0)
        
        # Total paid should be 500 (regular) + 200 (balance) = 700
        self.assertEqual(data['total_paid'], 700.0)
        
        # Balance due should be 1000 - 700 = 300
        self.assertEqual(data['balance_due'], 300.0)


class PaymentIntegrationTest(TestCase):
    """Integration tests for the payment system"""
    
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
    
    def test_create_regular_payment(self):
        """Test creating a regular payment through the form"""
        url = reverse('payment_create', args=[self.patient.id])
        
        # Form data for a regular payment
        data = {
            'payment_date': date.today().strftime('%Y-%m-%d'),
            'payment_method': 'cash',
            'total_amount': '1000.00',
            'amount_paid': '500.00',
            'notes': 'Test payment',
            
            # Formset data for payment items
            'items-TOTAL_FORMS': '1',
            'items-INITIAL_FORMS': '0',
            'items-MIN_NUM_FORMS': '0',
            'items-MAX_NUM_FORMS': '1000',
            'items-0-description': 'Test item',
            'items-0-amount': '500.00',
        }
        
        response = self.client.post(url, data, follow=True)
        
        # Check that the payment was created
        self.assertEqual(Payment.objects.count(), 1)
        payment = Payment.objects.first()
        
        # Check payment details
        self.assertEqual(payment.patient, self.patient)
        self.assertEqual(payment.total_amount, Decimal('1000.00'))
        self.assertEqual(payment.amount_paid, Decimal('500.00'))
        self.assertEqual(payment.payment_method, 'cash')
        self.assertEqual(payment.notes, 'Test payment')
        
        # Check payment item
        self.assertEqual(payment.items.count(), 1)
        item = payment.items.first()
        self.assertEqual(item.description, 'Test item')
        self.assertEqual(item.amount, Decimal('500.00'))
    
    def test_create_balance_payment(self):
        """Test creating a balance payment through the form"""
        # First create a regular payment to create a balance
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
        self.assertEqual(balance_payment.patient, self.patient)
        self.assertEqual(balance_payment.total_amount, Decimal('0.00'))
        self.assertEqual(balance_payment.amount_paid, Decimal('300.00'))
        self.assertEqual(balance_payment.payment_method, 'card')
        self.assertEqual(balance_payment.notes, 'Balance payment')
        
        # Check payment item
        self.assertEqual(balance_payment.items.count(), 1)
        item = balance_payment.items.first()
        self.assertEqual(item.description, 'Payment towards outstanding balance')
        self.assertEqual(item.amount, Decimal('300.00'))
        
        # Check that the balance is correctly calculated
        url = reverse('get_patient_balance', args=[self.patient.id])
        response = self.client.get(url)
        data = response.json()
        
        # Total amount should be 1000 (regular) + 0 (balance) = 1000
        self.assertEqual(data['total_treatment_cost'], 1000.0)
        
        # Total paid should be 500 (regular) + 300 (balance) = 800
        self.assertEqual(data['total_paid'], 800.0)
        
        # Balance due should be 1000 - 800 = 200
        self.assertEqual(data['balance_due'], 200.0) 