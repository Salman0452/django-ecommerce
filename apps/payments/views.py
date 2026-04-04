from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.orders.services import get_order_by_id
from .services import (
    create_payment,
    get_payment_by_id,
    get_payment_by_order,
    get_user_payments,
    update_payment_status,
)
from .models import Payment


class PaymentHistoryView(LoginRequiredMixin, ListView):
    """Display all payment records for the current user."""

    template_name = 'payments/payment_history.html'
    context_object_name = 'payments'

    def get_queryset(self):
        return get_user_payments(self.request.user)


class PaymentDetailView(LoginRequiredMixin, TemplateView):
    """Display details of a single payment."""

    template_name = 'payments/payment_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment'] = get_payment_by_id(self.kwargs['pk'], self.request.user)
        return context


class PaymentConfirmView(LoginRequiredMixin, View):
    """Initiate or confirm payment for a pending order.

    GET  — show a confirmation page with order summary and payment details.
    POST — process the payment (mark as completed) and redirect to payment detail.
    """

    template_name = 'payments/payment_confirm.html'

    def _get_or_init_payment(self, order):
        """Return the existing payment or create a new pending one."""
        payment = get_payment_by_order(order)
        if payment is None:
            payment = create_payment(order)
        return payment

    def get(self, request, order_id, *args, **kwargs):
        from django.shortcuts import render
        order = get_order_by_id(order_id, request.user)
        if order.status != 'pending':
            messages.error(request, 'This order cannot be paid.')
            return redirect('orders:order_detail', pk=order.pk)
        payment = self._get_or_init_payment(order)
        return render(request, self.template_name, {'payment': payment, 'order': order})

    def post(self, request, order_id, *args, **kwargs):
        order = get_order_by_id(order_id, request.user)
        if order.status != 'pending':
            messages.error(request, 'This order cannot be paid.')
            return redirect('orders:order_detail', pk=order.pk)

        payment = self._get_or_init_payment(order)
        if payment.status == Payment.STATUS_COMPLETED:
            messages.info(request, 'Payment has already been completed.')
            return redirect('payments:payment_detail', pk=payment.pk)

        update_payment_status(payment, Payment.STATUS_COMPLETED)
        messages.success(request, f'Payment for Order #{order.id} completed successfully!')
        return redirect('payments:payment_detail', pk=payment.pk)
