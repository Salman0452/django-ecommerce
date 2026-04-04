from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.orders.models import Cart, CartItem, Order
from apps.orders.services import add_item, get_or_create_cart
from apps.products.models import Category, Product
from apps.users.models import User


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
            price=Decimal('15.00'),
            category=category,
            stock=50,
        )

    def login(self):
        self.client.login(username='buyer@example.com', password='pass123')


class TestCartView(ViewTestBase):
    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get(reverse('orders:cart'))
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=' + reverse('orders:cart'),
        )

    def test_authenticated_returns_200(self):
        self.login()
        response = self.client.get(reverse('orders:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/cart.html')

    def test_empty_cart_shows_message(self):
        self.login()
        response = self.client.get(reverse('orders:cart'))
        self.assertContains(response, 'Your cart is empty.')


class TestAddToCartView(ViewTestBase):
    def test_unauthenticated_redirects(self):
        response = self.client.post(
            reverse('orders:cart_add'),
            {'product_id': self.product.id, 'quantity': 1},
        )
        self.assertEqual(response.status_code, 302)

    def test_adds_item_to_cart(self):
        self.login()
        self.client.post(
            reverse('orders:cart_add'),
            {'product_id': self.product.id, 'quantity': 2},
        )
        cart = get_or_create_cart(self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)

    def test_redirects_to_cart_after_adding(self):
        self.login()
        response = self.client.post(
            reverse('orders:cart_add'),
            {'product_id': self.product.id, 'quantity': 1},
        )
        self.assertRedirects(response, reverse('orders:cart'))

    def test_invalid_product_shows_error(self):
        self.login()
        response = self.client.post(
            reverse('orders:cart_add'),
            {'product_id': 99999, 'quantity': 1},
            follow=True,
        )
        self.assertContains(response, 'Product not found.')


class TestUpdateCartItemView(ViewTestBase):
    def setUp(self):
        super().setUp()
        self.login()
        cart = get_or_create_cart(self.user)
        add_item(cart, self.product.id, 1)

    def test_updates_quantity(self):
        self.client.post(
            reverse('orders:cart_update'),
            {'product_id': self.product.id, 'quantity': 5},
        )
        cart = get_or_create_cart(self.user)
        self.assertEqual(cart.items.first().quantity, 5)

    def test_redirects_to_cart(self):
        response = self.client.post(
            reverse('orders:cart_update'),
            {'product_id': self.product.id, 'quantity': 3},
        )
        self.assertRedirects(response, reverse('orders:cart'))

    def test_quantity_zero_removes_item(self):
        self.client.post(
            reverse('orders:cart_update'),
            {'product_id': self.product.id, 'quantity': 0},
        )
        cart = get_or_create_cart(self.user)
        self.assertEqual(cart.items.count(), 0)


class TestRemoveFromCartView(ViewTestBase):
    def setUp(self):
        super().setUp()
        self.login()
        cart = get_or_create_cart(self.user)
        add_item(cart, self.product.id, 1)

    def test_removes_item(self):
        self.client.post(
            reverse('orders:cart_remove'),
            {'product_id': self.product.id},
        )
        cart = get_or_create_cart(self.user)
        self.assertEqual(cart.items.count(), 0)

    def test_redirects_to_cart(self):
        response = self.client.post(
            reverse('orders:cart_remove'),
            {'product_id': self.product.id},
        )
        self.assertRedirects(response, reverse('orders:cart'))


class TestCheckoutView(ViewTestBase):
    def test_unauthenticated_redirects(self):
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 302)

    def test_get_returns_200_for_authenticated(self):
        self.login()
        cart = get_or_create_cart(self.user)
        add_item(cart, self.product.id, 1)
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/checkout.html')

    def test_post_creates_order_and_redirects(self):
        self.login()
        cart = get_or_create_cart(self.user)
        add_item(cart, self.product.id, 2)
        response = self.client.post(
            reverse('orders:checkout'),
            {'shipping_address': '1 Test Road, City'},
        )
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)
        self.assertRedirects(response, reverse('orders:order_detail', kwargs={'pk': order.pk}))

    def test_post_with_empty_cart_shows_error(self):
        self.login()
        response = self.client.post(
            reverse('orders:checkout'),
            {'shipping_address': '1 Test Road'},
            follow=True,
        )
        self.assertContains(response, 'empty cart')


class TestOrderHistoryView(ViewTestBase):
    def test_unauthenticated_redirects(self):
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_returns_200(self):
        self.login()
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_history.html')

    def test_shows_user_orders(self):
        self.login()
        cart = get_or_create_cart(self.user)
        add_item(cart, self.product.id, 1)
        from apps.orders.services import create_order
        create_order(self.user, '1 Test St')
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(len(response.context['orders']), 1)


class TestOrderDetailView(ViewTestBase):
    def setUp(self):
        super().setUp()
        self.login()
        cart = get_or_create_cart(self.user)
        add_item(cart, self.product.id, 1)
        from apps.orders.services import create_order
        self.order = create_order(self.user, '1 Test St')

    def test_returns_200_for_owner(self):
        response = self.client.get(reverse('orders:order_detail', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/order_detail.html')

    def test_shows_order_details(self):
        response = self.client.get(reverse('orders:order_detail', kwargs={'pk': self.order.pk}))
        self.assertContains(response, str(self.order.id))
        self.assertContains(response, '1 Test St')

    def test_returns_404_for_other_user(self):
        other = User.objects.create_user(
            email='other@example.com', username='other', password='pass'
        )
        self.client.login(username='other@example.com', password='pass')
        response = self.client.get(reverse('orders:order_detail', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 404)
