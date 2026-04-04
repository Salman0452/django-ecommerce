from django.urls import path

from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.AddToCartView.as_view(), name='cart_add'),
    path('cart/update/', views.UpdateCartItemView.as_view(), name='cart_update'),
    path('cart/remove/', views.RemoveFromCartView.as_view(), name='cart_remove'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('history/', views.OrderHistoryView.as_view(), name='order_history'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
]
