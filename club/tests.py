from datetime import timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

from .models import (
    TrainerProfile, ClientProfile, MembershipPlan, 
    Membership, Event, EventRegistration
)


class TrainerProfileTestCase(TestCase):
    """Test TrainerProfile model and operations"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='trainer1',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
        self.trainer = TrainerProfile.objects.create(
            user=self.user,
            display_name='Coach John',
            bio='Certified personal trainer',
            specialties='running, strength'
        )
    
    def test_trainer_profile_creation(self):
        """Test TrainerProfile is created correctly"""
        self.assertEqual(self.trainer.display_name, 'Coach John')
        self.assertEqual(self.trainer.specialties, 'running, strength')
    
    def test_trainer_str_with_display_name(self):
        """Test __str__ returns display_name when available"""
        self.assertEqual(str(self.trainer), 'Coach John')
    
    def test_trainer_str_fallback_to_full_name(self):
        """Test __str__ falls back to full name"""
        trainer2 = TrainerProfile.objects.create(user=self.user, display_name='')
        self.assertEqual(str(trainer2), 'John Doe')


class ClientProfileTestCase(TestCase):
    """Test ClientProfile model and properties"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        self.client_profile = self.user.client_profile
        
        # Create trainer
        trainer_user = User.objects.create_user(
            username='trainer1',
            password='testpass123'
        )
        self.trainer = TrainerProfile.objects.create(
            user=trainer_user,
            display_name='Coach'
        )
    
    def test_client_profile_auto_created(self):
        """Test ClientProfile is auto-created when user is created"""
        new_user = User.objects.create_user(
            username='newclient',
            password='testpass123'
        )
        self.assertTrue(hasattr(new_user, 'client_profile'))
    
    def test_client_default_level(self):
        """Test ClientProfile defaults to beginner level"""
        self.assertEqual(self.client_profile.level, 'beginner')
    
    def test_active_membership_property(self):
        """Test active_membership property returns current membership"""
        plan = MembershipPlan.objects.create(
            name='Monthly Plan',
            price=29.99,
            billing_interval='monthly'
        )
        today = timezone.now().date()
        membership = Membership.objects.create(
            user=self.user,
            plan=plan,
            start_date=today
        )
        
        self.assertEqual(self.client_profile.active_membership, membership)
    
    def test_has_active_membership_true(self):
        """Test has_active_membership returns True when active"""
        plan = MembershipPlan.objects.create(
            name='Monthly Plan',
            price=29.99,
            billing_interval='monthly'
        )
        today = timezone.now().date()
        Membership.objects.create(
            user=self.user,
            plan=plan,
            start_date=today
        )
        
        self.assertTrue(self.client_profile.has_active_membership)
    
    def test_has_active_membership_false(self):
        """Test has_active_membership returns False when no active membership"""
        self.assertFalse(self.client_profile.has_active_membership)
    
    def test_has_active_membership_expired(self):
        """Test has_active_membership returns False when membership expired"""
        plan = MembershipPlan.objects.create(
            name='Expired Plan',
            price=29.99,
            billing_interval='monthly'
        )
        past_date = timezone.now().date() - timedelta(days=60)
        Membership.objects.create(
            user=self.user,
            plan=plan,
            start_date=past_date
        )
        
        self.assertFalse(self.client_profile.has_active_membership)


class MembershipPlanTestCase(TestCase):
    """Test MembershipPlan model"""
    
    def setUp(self):
        """Create test data"""
        trainer_user = User.objects.create_user(
            username='trainer1',
            password='testpass123'
        )
        self.trainer = TrainerProfile.objects.create(user=trainer_user)
        self.plan = MembershipPlan.objects.create(
            trainer=self.trainer,
            name='Premium',
            price=49.99,
            billing_interval='monthly',
            is_active=True
        )
    
    def test_membership_plan_creation(self):
        """Test MembershipPlan creation"""
        self.assertEqual(self.plan.name, 'Premium')
        self.assertEqual(self.plan.price, 49.99)
        self.assertTrue(self.plan.is_active)
    
    def test_membership_plan_str(self):
        """Test __str__ method"""
        self.assertEqual(str(self.plan), 'Premium (monthly)')
    
    def test_membership_plan_yearly(self):
        """Test yearly billing interval"""
        yearly_plan = MembershipPlan.objects.create(
            trainer=self.trainer,
            name='Annual',
            price=499.99,
            billing_interval='yearly'
        )
        self.assertEqual(str(yearly_plan), 'Annual (yearly)')


class MembershipTestCase(TestCase):
    """Test Membership model and logic"""
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        self.plan = MembershipPlan.objects.create(
            name='Monthly Plan',
            price=29.99,
            billing_interval='monthly'
        )
        self.plan_yearly = MembershipPlan.objects.create(
            name='Yearly Plan',
            price=299.99,
            billing_interval='yearly'
        )
    
    def test_membership_auto_sets_end_date_monthly(self):
        """Test Membership auto-calculates end_date for monthly plan"""
        today = timezone.now().date()
        membership = Membership.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=today
        )
        
        expected_end = today + timedelta(days=30)
        self.assertEqual(membership.end_date, expected_end)
    
    def test_membership_auto_sets_end_date_yearly(self):
        """Test Membership auto-calculates end_date for yearly plan"""
        today = timezone.now().date()
        membership = Membership.objects.create(
            user=self.user,
            plan=self.plan_yearly,
            start_date=today
        )
        
        expected_end = today + timedelta(days=365)
        self.assertEqual(membership.end_date, expected_end)
    
    def test_membership_is_active_property_true(self):
        """Test is_active property returns True for current membership"""
        today = timezone.now().date()
        membership = Membership.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=today,
            status='active'
        )
        
        self.assertTrue(membership.is_active)
    
    def test_membership_is_active_property_false_expired(self):
        """Test is_active property returns False for expired membership"""
        today = timezone.now().date()
        past_start = today - timedelta(days=60)
        membership = Membership.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=past_start,
            status='active'
        )
        
        self.assertFalse(membership.is_active)
    
    def test_membership_str(self):
        """Test __str__ method"""
        today = timezone.now().date()
        membership = Membership.objects.create(
            user=self.user,
            plan=self.plan,
            start_date=today
        )
        
        expected_str = f"{self.user} - {self.plan.name} (active)"
        self.assertEqual(str(membership), expected_str)


class EventTestCase(TestCase):
    """Test Event model and properties"""
    
    def setUp(self):
        """Create test data"""
        trainer_user = User.objects.create_user(
            username='trainer1',
            password='testpass123'
        )
        self.trainer = TrainerProfile.objects.create(user=trainer_user)
        
        today = timezone.now()
        self.event = Event.objects.create(
            trainer=self.trainer,
            title='Running Club',
            description='Morning run',
            date=today.date() + timedelta(days=1),
            start_time=today.time(),
            event_type='running_club',
            distance_km=5.0,
            capacity=20
        )
    
    def test_event_creation(self):
        """Test Event creation"""
        self.assertEqual(self.event.title, 'Running Club')
        self.assertEqual(self.event.event_type, 'running_club')
        self.assertEqual(self.event.capacity, 20)
    
    def test_event_is_past_false(self):
        """Test is_past property for future event"""
        self.assertFalse(self.event.is_past)
    
    def test_event_is_past_true(self):
        """Test is_past property for past event"""
        past_date = timezone.now().date() - timedelta(days=1)
        past_event = Event.objects.create(
            trainer=self.trainer,
            title='Past Event',
            date=past_date,
            start_time=timezone.now().time(),
            capacity=20
        )
        
        self.assertTrue(past_event.is_past)
    
    def test_event_registrations_count(self):
        """Test registrations_count property"""
        client_user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        
        EventRegistration.objects.create(
            user=client_user,
            event=self.event,
            status='booked'
        )
        
        self.assertEqual(self.event.registrations_count, 1)
    
    def test_event_spots_left(self):
        """Test spots_left property"""
        client_user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        
        EventRegistration.objects.create(
            user=client_user,
            event=self.event,
            status='booked'
        )
        
        self.assertEqual(self.event.spots_left, 19)
    
    def test_event_is_full(self):
        """Test is_full property when at capacity"""
        small_event = Event.objects.create(
            trainer=self.trainer,
            title='Small Event',
            date=timezone.now().date() + timedelta(days=1),
            start_time=timezone.now().time(),
            capacity=1
        )
        
        client_user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        
        EventRegistration.objects.create(
            user=client_user,
            event=small_event,
            status='booked'
        )
        
        self.assertTrue(small_event.is_full)


class EventRegistrationTestCase(TestCase):
    """Test EventRegistration model"""
    
    def setUp(self):
        """Create test data"""
        self.client_user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        
        trainer_user = User.objects.create_user(
            username='trainer1',
            password='testpass123'
        )
        trainer = TrainerProfile.objects.create(user=trainer_user)
        
        today = timezone.now()
        self.event = Event.objects.create(
            trainer=trainer,
            title='Test Event',
            date=today.date() + timedelta(days=1),
            start_time=today.time(),
            capacity=20
        )
    
    def test_event_registration_creation(self):
        """Test EventRegistration creation"""
        registration = EventRegistration.objects.create(
            user=self.client_user,
            event=self.event,
            status='booked'
        )
        
        self.assertEqual(registration.status, 'booked')
        self.assertFalse(registration.attended)
    
    def test_event_registration_unique_constraint(self):
        """Test unique_together constraint prevents duplicate registration"""
        EventRegistration.objects.create(
            user=self.client_user,
            event=self.event
        )
        
        with self.assertRaises(Exception):
            EventRegistration.objects.create(
                user=self.client_user,
                event=self.event
            )
    
    def test_event_registration_str(self):
        """Test __str__ method"""
        registration = EventRegistration.objects.create(
            user=self.client_user,
            event=self.event
        )
        
        expected = f"{self.client_user} -> {self.event} (booked)"
        self.assertEqual(str(registration), expected)


class AuthenticationViewsTestCase(TestCase):
    """Test authentication and permission-based views"""
    
    def setUp(self):
        """Create test data"""
        self.client_obj = Client()
        self.client_user = User.objects.create_user(
            username='client1',
            password='testpass123'
        )
        trainer_user = User.objects.create_user(
            username='trainer1',
            password='testpass123'
        )
        self.trainer = TrainerProfile.objects.create(user=trainer_user)
    
    def test_membership_plans_view_accessible_anonymous(self):
        """Test membership_plans view is accessible without login"""
        response = self.client_obj.get(reverse('membership_plans'))
        self.assertEqual(response.status_code, 200)
    
    def test_exercise_plan_view_requires_login(self):
        """Test exercise_plan view requires authentication"""
        response = self.client_obj.get(reverse('exercise_plan'))
        self.assertNotEqual(response.status_code, 200)  # Should redirect or fail
    
    def test_exercise_plan_view_accessible_when_logged_in(self):
        """Test exercise_plan view is accessible when logged in"""
        self.client_obj.login(username='client1', password='testpass123')
        response = self.client_obj.get(reverse('exercise_plan'))
        self.assertEqual(response.status_code, 200)
    
    def test_client_dashboard_requires_login(self):
        """Test client_dashboard requires authentication"""
        response = self.client_obj.get(reverse('client_dashboard'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_trainer_dashboard_requires_login(self):
        """Test trainer_dashboard requires authentication"""
        response = self.client_obj.get(reverse('trainer_dashboard'))
        self.assertNotEqual(response.status_code, 200)


class FormValidationTestCase(TestCase):
    """Test form validation and error handling"""
    
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
    
    def test_membership_activation_without_client_profile(self):
        """Test membership activation fails for non-client user"""
        staff_user = User.objects.create_user(
            username='staff1',
            password='testpass123',
            is_staff=True
        )
        self.client_obj.login(username='staff1', password='testpass123')
        response = self.client_obj.post(
            reverse('activate_membership', args=[self.plan.id])
        )
        
        self.assertNotEqual(response.status_code, 200)
    
    def test_membership_activation_with_active_membership(self):
        """Test membership activation fails if user already has active membership"""
        today = timezone.now().date()
        Membership.objects.create(
            user=self.client_user,
            plan=self.plan,
            start_date=today
        )
        
        self.client_obj.login(username='client1', password='testpass123')
        response = self.client_obj.post(
            reverse('activate_membership', args=[self.plan.id])
        )
        
        # Should redirect or show error
        self.assertNotEqual(response.status_code, 200)
