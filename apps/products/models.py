from django.db import models
from apps.core.models import CoreModel

class Product(CoreModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='products'
    )
    is_active = models.BooleanField(default=True)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name