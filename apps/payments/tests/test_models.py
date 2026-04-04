from decimal import Decimal

from django.test import TestCase
from django.db.models import ProtectedError

from apps.users.models import User
from apps.orders.models import Order
from apps.payments.models import Payment


class PaymentModelTest(TestCase):
    """Test cases for the Payment model."""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
        )
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('99.99'),
            shipping_address='1 Test St',
        )

    def test_payment_creation(self):
        """Test creating a payment record."""
        payment = Payment.objects.create(
            order=self.order,
            amount=Decimal('99.99'),
        )
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.amount, Decimal('99.99'))
        self.assertEqual(payment.status, Payment.STATUS_PENDING)
        self.assertIsNotNone(payment.id)
        self.assertIsNotNone(payment.created_at)

    def test_payment_default_status_is_pending(self):
        """Test that the default status is pending."""
        payment = Payment.objects.create(order=self.order, amount=Decimal('10.00'))
        self.assertEqual(payment.status, 'pending')

    def test_payment_status_choices(self):
        """Test all valid status choices."""
        for status, _ in Payment.STATUS_CHOICES:
            order = Order.objects.create(
                user=self.user,
                total_price=Decimal('10.00'),
                shipping_address='Test St',
            )
            payment = Payment.objects.create(order=order, amount=Decimal('10.00'), status=status)
            self.assertEqual(payment.status, status)

    def test_payment_str_representation(self):
        """Test the string representation."""
        payment = Payment.objects.create(order=self.order, amount=Decimal('99.99'))
        self.assertIn(str(payment.id), str(payment))
        self.assertIn(str(self.order.id), str(payment))

    def test_payment_is_one_to_one_with_order(self):
        """Test that only one payment can exist per order."""
        from django.db import IntegrityError
        Payment.objects.create(order=self.order, amount=Decimal('99.99'))
        with self.assertRaises(IntegrityError):
            Payment.objects.create(order=self.order, amount=Decimal('99.99'))

    def test_payment_inherits_from_coremodel(self):
        """Test that Payment has CoreModel fields."""
        payment = Payment.objects.create(order=self.order, amount=Decimal('50.00'))
        self.assertIsNotNone(payment.created_at)
        self.assertIsNotNone(payment.updated_at)
        self.assertFalse(payment.is_deleted)

    def test_payment_soft_delete(self):
        """Test that is_deleted soft-deletes the payment."""
        payment = Payment.objects.create(order=self.order, amount=Decimal('50.00'))
        payment.is_deleted = True
        payment.save()
        self.assertTrue(Payment.objects.get(pk=payment.pk).is_deleted)

    def test_payment_order_protect(self):
        """Test that deleting an order with a payment is protected."""
        Payment.objects.create(order=self.order, amount=Decimal('99.99'))
        with self.assertRaises(ProtectedError):
            self.order.delete()

    def test_payment_related_name(self):
        """Test accessing payment via order.payment."""
        payment = Payment.objects.create(order=self.order, amount=Decimal('99.99'))
        self.assertEqual(self.order.payment, payment)

    def test_payment_default_ordering(self):
        """Test that payments are ordered by -created_at."""
        from django.utils import timezone
        from datetime import timedelta

        order2 = Order.objects.create(
            user=self.user,
            total_price=Decimal('10.00'),
            shipping_address='Test St',
        )
        p1 = Payment.objects.create(order=self.order, amount=Decimal('99.99'))
        Payment.objects.filter(pk=p1.pk).update(
            created_at=timezone.now() - timedelta(seconds=10)
        )
        p2 = Payment.objects.create(order=order2, amount=Decimal('10.00'))
        qs = Payment.objects.filter(order__user=self.user)
        self.assertEqual(qs.first().pk, p2.pk)
