from decimal import Decimal

from django.test import TestCase

from apps.orders.models import Cart, CartItem, Order, OrderItem
from apps.orders.services import (
    add_item,
    create_order,
    get_cart_total,
    get_order_by_id,
    get_or_create_cart,
    get_user_orders,
    remove_item,
    update_item_quantity,
)
from apps.products.models import Category, Product
from apps.users.models import User


class ServiceTestBase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='pass123',
        )
        category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            name='Widget',
            slug='widget',
            price=Decimal('10.00'),
            category=category,
            stock=100,
        )
        self.cart = get_or_create_cart(self.user)


class TestGetOrCreateCart(ServiceTestBase):
    def test_creates_cart_for_new_user(self):
        self.assertIsInstance(self.cart, Cart)
        self.assertEqual(self.cart.user, self.user)

    def test_returns_same_cart_on_repeat_call(self):
        cart2 = get_or_create_cart(self.user)
        self.assertEqual(self.cart.pk, cart2.pk)


class TestAddItem(ServiceTestBase):
    def test_adds_new_item_to_cart(self):
        item = add_item(self.cart, self.product.id, 2)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.product, self.product)

    def test_increases_quantity_for_existing_item(self):
        add_item(self.cart, self.product.id, 1)
        add_item(self.cart, self.product.id, 3)
        item = CartItem.objects.get(cart=self.cart, product=self.product)
        self.assertEqual(item.quantity, 4)

    def test_raises_for_inactive_product(self):
        self.product.is_active = False
        self.product.save()
        with self.assertRaises(Product.DoesNotExist):
            add_item(self.cart, self.product.id, 1)

    def test_raises_for_quantity_less_than_one(self):
        with self.assertRaises(ValueError):
            add_item(self.cart, self.product.id, 0)


class TestUpdateItemQuantity(ServiceTestBase):
    def setUp(self):
        super().setUp()
        add_item(self.cart, self.product.id, 2)

    def test_updates_quantity(self):
        item = update_item_quantity(self.cart, self.product.id, 5)
        self.assertEqual(item.quantity, 5)

    def test_removes_item_when_quantity_zero(self):
        update_item_quantity(self.cart, self.product.id, 0)
        self.assertFalse(CartItem.objects.filter(cart=self.cart, product=self.product).exists())

    def test_returns_none_for_missing_item(self):
        result = update_item_quantity(self.cart, 99999, 1)
        self.assertIsNone(result)


class TestRemoveItem(ServiceTestBase):
    def test_removes_existing_item(self):
        add_item(self.cart, self.product.id, 1)
        result = remove_item(self.cart, self.product.id)
        self.assertTrue(result)
        self.assertFalse(CartItem.objects.filter(cart=self.cart).exists())

    def test_returns_false_for_missing_item(self):
        result = remove_item(self.cart, self.product.id)
        self.assertFalse(result)


class TestGetCartTotal(ServiceTestBase):
    def test_total_of_empty_cart(self):
        self.assertEqual(get_cart_total(self.cart), Decimal('0.00'))

    def test_total_with_items(self):
        add_item(self.cart, self.product.id, 3)
        self.assertEqual(get_cart_total(self.cart), Decimal('30.00'))


class TestCreateOrder(ServiceTestBase):
    def test_creates_order_and_order_items(self):
        add_item(self.cart, self.product.id, 2)
        order = create_order(self.user, '123 Main St')
        self.assertIsInstance(order, Order)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.shipping_address, '123 Main St')
        self.assertEqual(order.total_price, Decimal('20.00'))
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, Decimal('10.00'))

    def test_clears_cart_after_order(self):
        add_item(self.cart, self.product.id, 1)
        create_order(self.user, '456 Oak Ave')
        self.assertEqual(self.cart.items.count(), 0)

    def test_raises_for_empty_cart(self):
        with self.assertRaises(ValueError):
            create_order(self.user, '789 Pine Rd')


class TestGetUserOrders(ServiceTestBase):
    def test_returns_orders_for_user(self):
        add_item(self.cart, self.product.id, 1)
        create_order(self.user, '1 Test St')
        orders = get_user_orders(self.user)
        self.assertEqual(orders.count(), 1)

    def test_excludes_deleted_orders(self):
        add_item(self.cart, self.product.id, 1)
        order = create_order(self.user, '1 Test St')
        order.is_deleted = True
        order.save()
        self.assertEqual(get_user_orders(self.user).count(), 0)


class TestGetOrderById(ServiceTestBase):
    def test_returns_order_for_owner(self):
        add_item(self.cart, self.product.id, 1)
        order = create_order(self.user, '1 Test St')
        fetched = get_order_by_id(order.id, self.user)
        self.assertEqual(fetched.pk, order.pk)

    def test_raises_404_for_wrong_user(self):
        from django.http import Http404
        add_item(self.cart, self.product.id, 1)
        order = create_order(self.user, '1 Test St')
        other_user = User.objects.create_user(
            email='other@example.com', username='other', password='pass'
        )
        with self.assertRaises(Http404):
            get_order_by_id(order.id, other_user)
