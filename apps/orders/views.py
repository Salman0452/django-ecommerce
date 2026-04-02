from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .services import get_or_create_cart


class CartView(LoginRequiredMixin, TemplateView):
    """Display the user's shopping cart."""
    
    template_name = 'orders/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request.user)
        context['cart'] = cart
        return context
