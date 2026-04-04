from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from apps.products.models import Category, Product
from apps.products.services import get_featured_products


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


class TestGetFeaturedProducts(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electronics', slug='electronics')

    def test_returns_4_most_recent_active_products(self):
        # Create 6 active products
        for i in range(6):
            Product.objects.create(
                category=self.category,
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('10.00'),
                stock=10,
                is_active=True,
            )

        featured = get_featured_products()

        self.assertEqual(len(featured), 4)
        # Most recent should be Product 5, 4, 3, 2 (created last)
        self.assertEqual(featured[0].name, 'Product 5')
        self.assertEqual(featured[3].name, 'Product 2')

    def test_excludes_inactive_products(self):
        # Create 3 active and 2 inactive products
        for i in range(3):
            Product.objects.create(
                category=self.category,
                name=f'Active Product {i}',
                slug=f'active-product-{i}',
                price=Decimal('10.00'),
                stock=10,
                is_active=True,
            )

        for i in range(2):
            Product.objects.create(
                category=self.category,
                name=f'Inactive Product {i}',
                slug=f'inactive-product-{i}',
                price=Decimal('10.00'),
                stock=10,
                is_active=False,
            )

        featured = get_featured_products()

        self.assertEqual(len(featured), 3)
        for product in featured:
            self.assertTrue(product.is_active)

    def test_excludes_deleted_products(self):
        # Create 3 active and 2 deleted products
        for i in range(3):
            Product.objects.create(
                category=self.category,
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('10.00'),
                stock=10,
                is_active=True,
                is_deleted=False,
            )

        for i in range(2):
            Product.objects.create(
                category=self.category,
                name=f'Deleted Product {i}',
                slug=f'deleted-product-{i}',
                price=Decimal('10.00'),
                stock=10,
                is_active=True,
                is_deleted=True,
            )

        featured = get_featured_products()

        self.assertEqual(len(featured), 3)
        for product in featured:
            self.assertFalse(product.is_deleted)

    def test_returns_less_than_4_when_fewer_products_exist(self):
        # Create only 2 products
        for i in range(2):
            Product.objects.create(
                category=self.category,
                name=f'Product {i}',
                slug=f'product-{i}',
                price=Decimal('10.00'),
                stock=10,
                is_active=True,
            )

        featured = get_featured_products()

        self.assertEqual(len(featured), 2)
