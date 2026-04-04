from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.users.models import User
from apps.orders.models import Order
from apps.orders.services import add_item, create_order, get_or_create_cart
from apps.products.models import Category, Product
from apps.payments.models import Payment
from apps.payments.services import create_payment


class ViewTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='buyer@example.com',
            username='buyer',
            password='pass123',
        )
        category = Category.objects.create(name='Gadgets', slug='gadgets')
        self.product = Product.objects.create(
            name='Gadget',
            slug='gadget',
            price=Decimal('25.00'),
            category=category,
            stock=50,
        )
        cart = get_or_create_cart(self.user)
        add_item(cart, self.product.id, 2)
        self.order = create_order(self.user, '1 Test Road')

    def login(self):
        self.client.login(username='buyer@example.com', password='pass123')


class TestPaymentHistoryView(ViewTestBase):
    def test_unauthenticated_redirects(self):
        response = self.client.get(reverse('payments:payment_history'))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_returns_200(self):
        self.login()
        response = self.client.get(reverse('payments:payment_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/payment_history.html')

    def test_shows_user_payments(self):
        self.login()
        create_payment(self.order)
        response = self.client.get(reverse('payments:payment_history'))
        self.assertEqual(len(response.context['payments']), 1)

    def test_empty_payment_history(self):
        self.login()
        response = self.client.get(reverse('payments:payment_history'))
        self.assertContains(response, 'no payment records')


class TestPaymentDetailView(ViewTestBase):
    def setUp(self):
        super().setUp()
        self.payment = create_payment(self.order)

    def test_unauthenticated_redirects(self):
        response = self.client.get(
            reverse('payments:payment_detail', kwargs={'pk': self.payment.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_authenticated_returns_200(self):
        self.login()
        response = self.client.get(
            reverse('payments:payment_detail', kwargs={'pk': self.payment.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/payment_detail.html')

    def test_shows_payment_details(self):
        self.login()
        response = self.client.get(
            reverse('payments:payment_detail', kwargs={'pk': self.payment.pk})
        )
        self.assertContains(response, str(self.payment.id))
        self.assertContains(response, str(self.order.id))

    def test_returns_404_for_other_user(self):
        other = User.objects.create_user(
            email='other@example.com', username='other', password='pass'
        )
        self.client.login(username='other@example.com', password='pass')
        response = self.client.get(
            reverse('payments:payment_detail', kwargs={'pk': self.payment.pk})
        )
        self.assertEqual(response.status_code, 404)


class TestPaymentConfirmView(ViewTestBase):
    def test_unauthenticated_redirects(self):
        response = self.client.get(
            reverse('payments:payment_confirm', kwargs={'order_id': self.order.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_get_returns_200_for_authenticated(self):
        self.login()
        response = self.client.get(
            reverse('payments:payment_confirm', kwargs={'order_id': self.order.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/payment_confirm.html')

    def test_get_creates_pending_payment(self):
        self.login()
        self.client.get(
            reverse('payments:payment_confirm', kwargs={'order_id': self.order.pk})
        )
        self.assertTrue(Payment.objects.filter(order=self.order).exists())

    def test_post_completes_payment_and_redirects(self):
        self.login()
        response = self.client.post(
            reverse('payments:payment_confirm', kwargs={'order_id': self.order.pk})
        )
        payment = Payment.objects.get(order=self.order)
        self.assertEqual(payment.status, Payment.STATUS_COMPLETED)
        self.assertRedirects(
            response,
            reverse('payments:payment_detail', kwargs={'pk': payment.pk}),
        )

    def test_post_marks_order_as_paid(self):
        self.login()
        self.client.post(
            reverse('payments:payment_confirm', kwargs={'order_id': self.order.pk})
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')

    def test_post_on_already_paid_order_redirects_with_message(self):
        self.login()
        payment = create_payment(self.order)
        payment.status = Payment.STATUS_COMPLETED
        payment.save()
        self.order.status = 'paid'
        self.order.save()
        response = self.client.post(
            reverse('payments:payment_confirm', kwargs={'order_id': self.order.pk}),
            follow=True,
        )
        self.assertContains(response, 'cannot be paid')

    def test_returns_404_for_other_users_order(self):
        other = User.objects.create_user(
            email='other@example.com', username='other', password='pass'
        )
        self.client.login(username='other@example.com', password='pass')
        response = self.client.get(
            reverse('payments:payment_confirm', kwargs={'order_id': self.order.pk})
        )
        self.assertEqual(response.status_code, 404)
