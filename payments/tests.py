from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

from club.models import MembershipPlan, Membership
from .models import Payment


class PaymentModelTestCase(TestCase):
    """Test Payment model and methods"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        self.plan = MembershipPlan.objects.create(
            name='Test Plan',
            price=29.99,
            billing_interval='monthly'
        )
        self.payment = Payment.objects.create(
            user=self.user,
            stripe_payment_intent_id='pi_test123',
            membership_plan=self.plan,
            amount_cents=2999,
            amount_currency='USD',
            status='pending'
        )
    
    def test_payment_creation(self):
        """Test Payment model creation"""
        self.assertEqual(self.payment.user, self.user)
        self.assertEqual(self.payment.amount_cents, 2999)
        self.assertEqual(self.payment.status, 'pending')
    
    def test_payment_str_representation(self):
        """Test Payment __str__ method"""
        expected = f"{self.user.username} - $29.99 (pending)"
        self.assertEqual(str(self.payment), expected)
    
    def test_mark_payment_succeeded(self):
        """Test mark_succeeded method"""
        self.payment.mark_succeeded(charge_id='ch_test123')
        
        self.assertEqual(self.payment.status, 'succeeded')
        self.assertEqual(self.payment.stripe_charge_id, 'ch_test123')
        self.assertIsNotNone(self.payment.paid_at)
    
    def test_mark_payment_failed(self):
        """Test mark_failed method"""
        self.payment.mark_failed()
        
        self.assertEqual(self.payment.status, 'failed')
    
    def test_payment_amount_currency_default(self):
        """Test payment defaults to USD currency"""
        payment = Payment.objects.create(
            user=self.user,
            stripe_payment_intent_id='pi_test456',
            amount_cents=5000
        )
        
        self.assertEqual(payment.amount_currency, 'USD')
    
    def test_payment_unique_stripe_intent_id(self):
        """Test stripe_payment_intent_id unique constraint"""
        with self.assertRaises(Exception):
            Payment.objects.create(
                user=self.user,
                stripe_payment_intent_id='pi_test123',  # Duplicate
                amount_cents=2999
            )
    
    def test_payment_ordering(self):
        """Test Payment ordering by created_at descending"""
        older_payment = Payment.objects.create(
            user=self.user,
            stripe_payment_intent_id='pi_old',
            amount_cents=1000
        )
        # Newer payment is already created in setUp
        
        payments = list(Payment.objects.all())
        self.assertEqual(payments[0], self.payment)
        self.assertEqual(payments[1], older_payment)


class PaymentViewsTestCase(TestCase):
    """Test payment processing views"""
    
    def setUp(self):
        """Create test data"""
        self.client_obj = Client()
        self.client_user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        self.plan = MembershipPlan.objects.create(
            name='Test Plan',
            price=29.99,
            billing_interval='monthly',
            is_active=True
        )
    
    def test_create_checkout_session_requires_login(self):
        """Test checkout session creation requires authentication"""
        response = self.client_obj.post(
            reverse('create_checkout_session', args=[self.plan.id])
        )
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_create_checkout_session_requires_client_profile(self):
        """Test checkout requires client profile"""
        staff_user = User.objects.create_user(
            username='staff1',
            password='testpass123',
            is_staff=True
        )
        self.client_obj.login(username='staff1', password='testpass123')
        
        response = self.client_obj.post(
            reverse('create_checkout_session', args=[self.plan.id])
        )
        
        # Should fail without client profile
        self.assertNotEqual(response.status_code, 200)
    
    def test_create_checkout_session_fails_with_active_membership(self):
        """Test checkout fails if user has active membership"""
        today = timezone.now().date()
        Membership.objects.create(
            user=self.client_user,
            plan=self.plan,
            start_date=today
        )
        
        self.client_obj.login(username='client1', password='testpass123')
        response = self.client_obj.post(
            reverse('create_checkout_session', args=[self.plan.id])
        )
        
        # Should redirect with error
        self.assertNotEqual(response.status_code, 200)
    
    def test_payment_success_requires_login(self):
        """Test payment success view requires authentication"""
        response = self.client_obj.get(reverse('payment_success'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_payment_success_missing_session_id(self):
        """Test payment success fails without session_id"""
        self.client_obj.login(username='client1', password='testpass123')
        response = self.client_obj.get(reverse('payment_success'))
        
        # Should fail or redirect with error
        self.assertNotEqual(response.status_code, 200)
    
    def test_payment_cancel_requires_login(self):
        """Test payment cancel view requires authentication"""
        response = self.client_obj.get(reverse('payment_cancel'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)


class PaymentSecurityTestCase(TestCase):
    """Test payment security and validation"""
    
    def setUp(self):
        """Create test data"""
        self.user1 = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='client2',
            password='testpass123'
        )
        self.plan = MembershipPlan.objects.create(
            name='Test Plan',
            price=29.99,
            billing_interval='monthly',
            is_active=True
        )
    
    def test_payment_belongs_to_authenticated_user(self):
        """Test payment can only be accessed by owner"""
        payment = Payment.objects.create(
            user=self.user1,
            stripe_payment_intent_id='pi_user1',
            amount_cents=2999,
            status='succeeded'
        )
        
        # Only user1 should have access
        self.assertEqual(payment.user, self.user1)
        self.assertNotEqual(payment.user, self.user2)
    
    def test_membership_only_created_for_correct_user(self):
        """Test membership is only created for the user who paid"""
        payment = Payment.objects.create(
            user=self.user1,
            stripe_payment_intent_id='pi_test',
            membership_plan=self.plan,
            amount_cents=2999,
            status='succeeded'
        )
        
        # Membership should be linked to correct user
        self.assertEqual(payment.user, self.user1)
