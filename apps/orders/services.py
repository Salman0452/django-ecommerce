from decimal import Decimal
from django.db import transaction
from django.http import Http404

from .models import Cart, CartItem, Order, OrderItem
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
        quantity: The quantity to add (must be >= 1)

    Returns:
        CartItem: The updated or created CartItem

    Raises:
        Product.DoesNotExist: If the product does not exist
        ValueError: If quantity is less than 1
    """
    if quantity < 1:
        raise ValueError('Quantity must be at least 1.')
    product = Product.objects.get(id=product_id, is_active=True, is_deleted=False)

    with transaction.atomic():
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item


def update_item_quantity(cart, product_id, quantity):
    """Set the quantity of a cart item directly.  Removes the item if quantity <= 0.

    Args:
        cart: The Cart instance
        product_id: The Product ID whose quantity should be updated
        quantity: The new quantity (removes item when <= 0)

    Returns:
        CartItem | None: The updated CartItem, or None if the item was removed
    """
    try:
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
    except CartItem.DoesNotExist:
        return None

    if quantity <= 0:
        cart_item.delete()
        return None

    cart_item.quantity = quantity
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


def create_order(user, shipping_address):
    """Create a new order from the user's cart and clear the cart.

    Args:
        user: The User instance
        shipping_address: Shipping address string

    Returns:
        Order: The newly created Order

    Raises:
        ValueError: If the cart is empty
    """
    cart = get_or_create_cart(user)
    items = list(cart.items.filter(is_deleted=False).select_related('product'))

    if not items:
        raise ValueError('Cannot create an order from an empty cart.')

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            total_price=cart.total,
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )

        cart.items.all().delete()

    return order


def get_user_orders(user):
    """Return all non-deleted orders for the given user, newest first.

    Args:
        user: The User instance

    Returns:
        QuerySet: Ordered queryset of Order instances
    """
    return Order.objects.filter(user=user, is_deleted=False).prefetch_related('items__product').order_by('-created_at')


def get_order_by_id(order_id, user):
    """Return a single order belonging to the user.

    Args:
        order_id: The Order primary key
        user: The User instance (ownership check)

    Returns:
        Order: The matching Order

    Raises:
        Http404: If the order does not exist or belongs to another user
    """
    try:
        return Order.objects.prefetch_related('items__product').get(
            id=order_id, user=user, is_deleted=False
        )
    except Order.DoesNotExist as exc:
        raise Http404('Order not found.') from exc
