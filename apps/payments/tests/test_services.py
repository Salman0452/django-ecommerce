from decimal import Decimal

from django.http import Http404
from django.test import TestCase

from apps.users.models import User
from apps.orders.models import Order
from apps.payments.models import Payment
from apps.payments.services import (
    create_payment,
    get_payment_by_id,
    get_payment_by_order,
    get_user_payments,
    update_payment_status,
)


class ServiceTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='buyer@example.com',
            username='buyer',
            password='pass123',
        )
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('49.99'),
            shipping_address='1 Service St',
        )


class TestCreatePayment(ServiceTestBase):
    def test_creates_pending_payment(self):
        payment = create_payment(self.order)
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.amount, self.order.total_price)
        self.assertEqual(payment.status, Payment.STATUS_PENDING)

    def test_raises_if_payment_already_exists(self):
        create_payment(self.order)
        with self.assertRaises(ValueError):
            create_payment(self.order)


class TestGetPaymentByOrder(ServiceTestBase):
    def test_returns_payment_if_exists(self):
        payment = Payment.objects.create(order=self.order, amount=Decimal('49.99'))
        result = get_payment_by_order(self.order)
        self.assertEqual(result, payment)

    def test_returns_none_if_no_payment(self):
        result = get_payment_by_order(self.order)
        self.assertIsNone(result)


class TestUpdatePaymentStatus(ServiceTestBase):
    def setUp(self):
        super().setUp()
        self.payment = create_payment(self.order)

    def test_updates_status_to_completed(self):
        self.order.refresh_from_db()
        update_payment_status(self.payment, Payment.STATUS_COMPLETED)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.STATUS_COMPLETED)

    def test_completed_payment_marks_order_as_paid(self):
        update_payment_status(self.payment, Payment.STATUS_COMPLETED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')

    def test_updates_status_to_failed(self):
        update_payment_status(self.payment, Payment.STATUS_FAILED)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.STATUS_FAILED)

    def test_failed_payment_does_not_change_order_status(self):
        update_payment_status(self.payment, Payment.STATUS_FAILED)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'pending')

    def test_raises_on_invalid_status(self):
        with self.assertRaises(ValueError):
            update_payment_status(self.payment, 'invalid_status')


class TestGetUserPayments(ServiceTestBase):
    def test_returns_payments_for_user(self):
        Payment.objects.create(order=self.order, amount=Decimal('49.99'))
        results = get_user_payments(self.user)
        self.assertEqual(results.count(), 1)

    def test_excludes_deleted_payments(self):
        payment = Payment.objects.create(order=self.order, amount=Decimal('49.99'))
        payment.is_deleted = True
        payment.save()
        self.assertEqual(get_user_payments(self.user).count(), 0)

    def test_excludes_other_users_payments(self):
        other = User.objects.create_user(
            email='other@example.com', username='other', password='pass'
        )
        other_order = Order.objects.create(
            user=other, total_price=Decimal('10.00'), shipping_address='Other St'
        )
        Payment.objects.create(order=other_order, amount=Decimal('10.00'))
        self.assertEqual(get_user_payments(self.user).count(), 0)


class TestGetPaymentById(ServiceTestBase):
    def test_returns_payment_for_owner(self):
        payment = Payment.objects.create(order=self.order, amount=Decimal('49.99'))
        result = get_payment_by_id(payment.id, self.user)
        self.assertEqual(result, payment)

    def test_raises_404_for_wrong_user(self):
        other = User.objects.create_user(
            email='other@example.com', username='other', password='pass'
        )
        payment = Payment.objects.create(order=self.order, amount=Decimal('49.99'))
        with self.assertRaises(Http404):
            get_payment_by_id(payment.id, other)

    def test_raises_404_for_nonexistent_id(self):
        with self.assertRaises(Http404):
            get_payment_by_id(99999, self.user)
