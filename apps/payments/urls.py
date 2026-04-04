from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.PaymentHistoryView.as_view(), name='payment_history'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment_detail'),
    path('pay/<int:order_id>/', views.PaymentConfirmView.as_view(), name='payment_confirm'),
]
