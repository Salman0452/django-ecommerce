from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from apps.products.models import Category, Product


class TestCategoryModel(TestCase):
    def test_str(self):
        category = Category.objects.create(name='Electronics', slug='electronics')

        self.assertEqual(str(category), 'Electronics')

    def test_slug_uniqueness(self):
        Category.objects.create(name='Electronics', slug='electronics')

        with self.assertRaises(IntegrityError):
            Category.objects.create(name='Home', slug='electronics')


class TestProductModel(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Books', slug='books')

    def test_str(self):
        product = Product.objects.create(
            category=self.category,
            name='Django Book',
            slug='django-book',
            description='Comprehensive Django guide',
            price=Decimal('49.99'),
            stock=20,
        )

        self.assertEqual(str(product), 'Django Book')

    def test_is_active_default_true(self):
        product = Product.objects.create(
            category=self.category,
            name='Python Book',
            slug='python-book',
            description='Python fundamentals',
            price=Decimal('29.99'),
            stock=15,
        )

        self.assertTrue(product.is_active)

    def test_price_field(self):
        product = Product.objects.create(
            category=self.category,
            name='Data Science Book',
            slug='data-science-book',
            description='Data science concepts',
            price=Decimal('199.99'),
            stock=5,
        )

        price_field = Product._meta.get_field('price')
        self.assertEqual(price_field.max_digits, 10)
        self.assertEqual(price_field.decimal_places, 2)
        self.assertEqual(product.price, Decimal('199.99'))
