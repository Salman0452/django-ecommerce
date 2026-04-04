from django.db import transaction
from django.http import Http404

from .models import Payment
from apps.orders.models import Order


def create_payment(order):
    """Create a pending payment record for the given order.

    Args:
        order: The Order instance to pay for

    Returns:
        Payment: The newly created Payment

    Raises:
        ValueError: If a payment already exists for this order
    """
    if Payment.objects.filter(order=order).exists():
        raise ValueError(f'A payment already exists for Order #{order.id}.')

    payment = Payment.objects.create(
        order=order,
        amount=order.total_price,
        status=Payment.STATUS_PENDING,
    )
    return payment


def get_payment_by_order(order):
    """Return the payment record for the given order, or None.

    Args:
        order: The Order instance

    Returns:
        Payment | None: The Payment if it exists, otherwise None
    """
    try:
        return Payment.objects.get(order=order)
    except Payment.DoesNotExist:
        return None


def update_payment_status(payment, status):
    """Update a payment's status and keep the linked order's status in sync.

    When a payment is marked completed the order is set to 'paid'.
    When a payment is marked failed the order remains unchanged.

    Args:
        payment: The Payment instance to update
        status: One of Payment.STATUS_PENDING / STATUS_COMPLETED / STATUS_FAILED

    Returns:
        Payment: The updated Payment

    Raises:
        ValueError: If status is not a valid choice
    """
    valid_statuses = {choice[0] for choice in Payment.STATUS_CHOICES}
    if status not in valid_statuses:
        raise ValueError(f"Invalid payment status: '{status}'.")

    with transaction.atomic():
        payment.status = status
        payment.save()

        if status == Payment.STATUS_COMPLETED:
            Order.objects.filter(pk=payment.order_id).update(status='paid')
            payment.order.refresh_from_db()

    return payment


def get_user_payments(user):
    """Return all non-deleted payments for the given user, newest first.

    Args:
        user: The User instance

    Returns:
        QuerySet: Ordered queryset of Payment instances
    """
    return (
        Payment.objects
        .filter(order__user=user, is_deleted=False)
        .select_related('order')
        .order_by('-created_at')
    )


def get_payment_by_id(payment_id, user):
    """Return a single payment belonging to the given user.

    Args:
        payment_id: The Payment primary key
        user: The User instance (ownership check)

    Returns:
        Payment: The matching Payment

    Raises:
        Http404: If the payment does not exist or belongs to another user
    """
    try:
        return Payment.objects.select_related('order').get(
            id=payment_id,
            order__user=user,
            is_deleted=False,
        )
    except Payment.DoesNotExist as exc:
        raise Http404('Payment not found.') from exc
