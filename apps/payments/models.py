from decimal import Decimal
from django.db import models
from apps.core.models import CoreModel


class Payment(CoreModel):
    """Payment record linked to an order."""

    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.PROTECT,
        related_name='payment',
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Payment #{self.id} — Order #{self.order_id} [{self.get_status_display()}]"
