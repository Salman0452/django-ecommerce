from decimal import Decimal
from django.db import transaction

from .models import Cart, CartItem
from apps.products.models import Product


def get_or_create_cart(user):
    """Get or create the user's active cart.
    
    Args:
        user: The User instance
        
    Returns:
        Cart: The user's cart
    """
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


def add_item(cart, product_id, quantity):
    """Add or update an item in the cart.
    
    Args:
        cart: The Cart instance
        product_id: The Product ID to add
        quantity: The quantity to add
        
    Returns:
        CartItem: The updated or created CartItem
        
    Raises:
        Product.DoesNotExist: If the product does not exist
    """
    product = Product.objects.get(id=product_id)
    
    with transaction.atomic():
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            # Update quantity if item already exists
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item


def remove_item(cart, product_id):
    """Remove an item from the cart.
    
    Args:
        cart: The Cart instance
        product_id: The Product ID to remove
        
    Returns:
        bool: True if item was removed, False if item did not exist
    """
    deleted_count, _ = CartItem.objects.filter(
        cart=cart,
        product_id=product_id
    ).delete()
    return deleted_count > 0


def get_cart_total(cart):
    """Calculate the total price of the cart.
    
    Args:
        cart: The Cart instance
        
    Returns:
        Decimal: The total price of all items in the cart
    """
    return cart.total
