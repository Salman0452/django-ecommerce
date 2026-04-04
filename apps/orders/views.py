from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView, ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CheckoutForm
from .services import (
    add_item,
    create_order,
    get_or_create_cart,
    get_order_by_id,
    get_user_orders,
    remove_item,
    update_item_quantity,
)
from apps.products.models import Product


class CartView(LoginRequiredMixin, TemplateView):
    """Display the user's shopping cart."""

    template_name = 'orders/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request.user)
        context['cart'] = cart
        return context


class AddToCartView(LoginRequiredMixin, View):
    """Add a product to the user's cart."""

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request.user)
        product_id = request.POST.get('product_id')
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1

        try:
            add_item(cart, product_id, quantity)
            messages.success(request, 'Item added to cart.')
        except Product.DoesNotExist:
            messages.error(request, 'Product not found.')
        except ValueError as exc:
            messages.error(request, str(exc))

        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or ''
        if next_url.startswith('/'):
            return redirect(next_url)
        return redirect('orders:cart')


class UpdateCartItemView(LoginRequiredMixin, View):
    """Update the quantity of a cart item."""

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request.user)
        product_id = request.POST.get('product_id')
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1

        update_item_quantity(cart, product_id, quantity)
        return redirect('orders:cart')


class RemoveFromCartView(LoginRequiredMixin, View):
    """Remove a product from the user's cart."""

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        cart = get_or_create_cart(request.user)
        product_id = request.POST.get('product_id')
        remove_item(cart, product_id)
        messages.success(request, 'Item removed from cart.')
        return redirect('orders:cart')


class CheckoutView(LoginRequiredMixin, FormView):
    """Display and process the checkout form."""

    template_name = 'orders/checkout.html'
    form_class = CheckoutForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = get_or_create_cart(self.request.user)
        return context

    def form_valid(self, form):
        try:
            order = create_order(
                user=self.request.user,
                shipping_address=form.cleaned_data['shipping_address'],
            )
            messages.success(self.request, f'Order #{order.id} placed successfully!')
            return redirect('orders:order_detail', pk=order.pk)
        except ValueError as exc:
            messages.error(self.request, str(exc))
            return self.form_invalid(form)


class OrderHistoryView(LoginRequiredMixin, ListView):
    """Display the user's order history."""

    template_name = 'orders/order_history.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return get_user_orders(self.request.user)


class OrderDetailView(LoginRequiredMixin, TemplateView):
    """Display details of a single order."""

    template_name = 'orders/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_order_by_id(kwargs['pk'], self.request.user)
        return context
