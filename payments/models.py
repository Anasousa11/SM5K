from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from club.models import MembershipPlan


class Payment(models.Model):
    """
    Record of a Stripe payment transaction.
    Tracks successful payments for membership purchases and premium features.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True)
    
    membership_plan = models.ForeignKey(
        MembershipPlan, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='payments'
    )
    
    amount_cents = models.PositiveIntegerField()  # Amount in cents (Stripe format)
    amount_currency = models.CharField(max_length=3, default='USD')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata for webhook processing
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]
    
    def __str__(self):
        amount_usd = f"${self.amount_cents / 100:.2f}"
        return f"{self.user.username} - {amount_usd} ({self.status})"
    
    def mark_succeeded(self, charge_id=None):
        """Mark payment as successfully completed."""
        self.status = 'succeeded'
        self.paid_at = timezone.now()
        if charge_id:
            self.stripe_charge_id = charge_id
        self.save()
    
    def mark_failed(self):
        """Mark payment as failed."""
        self.status = 'failed'
        self.save()


class Invoice(models.Model):
    """
    Invoice records for tracking membership renewals and transactions.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    payment = models.OneToOneField(
        Payment, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='invoice'
    )
    
    invoice_number = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    
    amount_cents = models.PositiveIntegerField()
    tax_cents = models.PositiveIntegerField(default=0)
    total_cents = models.PositiveIntegerField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    issued_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField()
    paid_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.user.username}"
