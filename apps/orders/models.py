from django.db import models
from apps.core.models import CoreModel


class Cart(CoreModel):
    """Shopping cart for a user."""
    
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='cart'
    )
    
    def __str__(self):
        return f"Cart - {self.user.email}"
    
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
    
    @property
    def total(self):
        """Calculate total price of all items in cart."""
        from decimal import Decimal
        return sum(
            item.product.price * item.quantity 
            for item in self.items.filter(is_deleted=False)
        ) or Decimal('0.00')
    
    @property
    def item_count(self):
        """Get total count of items in cart."""
        return sum(
            item.quantity 
            for item in self.items.filter(is_deleted=False)
        )


class CartItem(CoreModel):
    """Item in a shopping cart."""
    
    cart = models.ForeignKey(
        'orders.Cart',
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ('cart', 'product')
        indexes = [
            models.Index(fields=['cart_id']),
        ]


class Order(CoreModel):
    """Order model representing a customer's purchase."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='orders'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    shipping_address = models.TextField()
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['-created_at']),
        ]
