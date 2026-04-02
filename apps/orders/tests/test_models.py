from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from decimal import Decimal

from apps.users.models import User
from apps.orders.models import Order


class OrderModelTest(TestCase):
    """Test cases for the Order model."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

    def test_order_creation(self):
        """Test creating a new order."""
        order = Order.objects.create(
            user=self.user,
            status='pending',
            total_price=Decimal('99.99'),
            shipping_address='123 Main St, City, State 12345'
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.total_price, Decimal('99.99'))
        self.assertIsNotNone(order.id)
        self.assertIsNotNone(order.created_at)

    def test_order_str_representation(self):
        """Test the string representation of an order."""
        order = Order.objects.create(
            user=self.user,
            status='paid',
            total_price=Decimal('150.00'),
            shipping_address='456 Oak Ave, Town, State 67890'
        )
        expected_str = f"Order #{order.id} - {self.user.email}"
        self.assertEqual(str(order), expected_str)

    def test_order_status_choices(self):
        """Test that only valid status choices are accepted."""
        valid_statuses = ['pending', 'paid', 'shipped', 'completed', 'cancelled']
        for status in valid_statuses:
            order = Order.objects.create(
                user=self.user,
                status=status,
                total_price=Decimal('50.00'),
                shipping_address='789 Pine Rd'
            )
            self.assertEqual(order.status, status)

    def test_order_default_status(self):
        """Test that order status defaults to 'pending'."""
        order = Order.objects.create(
            user=self.user,
            total_price=Decimal('75.00'),
            shipping_address='100 Elm St'
        )
        self.assertEqual(order.status, 'pending')

    def test_order_total_price_decimal_precision(self):
        """Test that total_price maintains decimal precision."""
        order = Order.objects.create(
            user=self.user,
            status='paid',
            total_price=Decimal('123.45'),
            shipping_address='200 Maple Dr'
        )
        self.assertEqual(order.total_price, Decimal('123.45'))

    def test_order_shipping_address_required(self):
        """Test that shipping_address is required."""
        with self.assertRaises(ValueError):
            Order.objects.create(
                user=self.user,
                status='pending',
                total_price=Decimal('50.00'),
                shipping_address=''
            )

    def test_order_user_foreignkey_protect(self):
        """Test that deleting user is protected when orders exist."""
        order = Order.objects.create(
            user=self.user,
            status='pending',
            total_price=Decimal('100.00'),
            shipping_address='300 Cedar Ln'
        )
        with self.assertRaises(ProtectedError):
            self.user.delete()

    def test_order_related_name(self):
        """Test that orders are accessible via user.orders."""
        order1 = Order.objects.create(
            user=self.user,
            status='pending',
            total_price=Decimal('50.00'),
            shipping_address='400 Birch St'
        )
        order2 = Order.objects.create(
            user=self.user,
            status='paid',
            total_price=Decimal('75.00'),
            shipping_address='500 Spruce Ave'
        )
        self.assertEqual(self.user.orders.count(), 2)
        self.assertIn(order1, self.user.orders.all())
        self.assertIn(order2, self.user.orders.all())

    def test_order_default_ordering(self):
        """Test that orders are ordered by -created_at by default."""
        order1 = Order.objects.create(
            user=self.user,
            status='pending',
            total_price=Decimal('50.00'),
            shipping_address='600 Ash Ct'
        )
        order2 = Order.objects.create(
            user=self.user,
            status='paid',
            total_price=Decimal('100.00'),
            shipping_address='700 Walnut Blvd'
        )
        orders = Order.objects.all()
        self.assertEqual(orders.first().id, order2.id)
        self.assertEqual(orders.last().id, order1.id)

    def test_order_inherits_from_coremodel(self):
        """Test that Order has CoreModel fields."""
        order = Order.objects.create(
            user=self.user,
            status='pending',
            total_price=Decimal('60.00'),
            shipping_address='800 Oak Ridge Rd'
        )
        self.assertIsNotNone(order.id)
        self.assertIsNotNone(order.created_at)
        self.assertIsNotNone(order.updated_at)
        self.assertFalse(order.is_deleted)

    def test_order_soft_delete(self):
        """Test that is_deleted soft deletes orders."""
        order = Order.objects.create(
            user=self.user,
            status='pending',
            total_price=Decimal('70.00'),
            shipping_address='900 Sycamore St'
        )
        order.is_deleted = True
        order.save()
        self.assertTrue(order.is_deleted)
        self.assertTrue(Order.objects.filter(id=order.id, is_deleted=True).exists())

    def test_order_multiple_users(self):
        """Test that multiple users can have orders."""
        user2 = User.objects.create_user(
            email='test2@example.com',
            username='testuser2',
            password='testpass123'
        )
        order1 = Order.objects.create(
            user=self.user,
            status='pending',
            total_price=Decimal('50.00'),
            shipping_address='1000 Dogwood Ln'
        )
        order2 = Order.objects.create(
            user=user2,
            status='paid',
            total_price=Decimal('100.00'),
            shipping_address='1100 Hickory Ave'
        )
        self.assertEqual(self.user.orders.count(), 1)
        self.assertEqual(user2.orders.count(), 1)
        self.assertEqual(order1.user, self.user)
        self.assertEqual(order2.user, user2)
