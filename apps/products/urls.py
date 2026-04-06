from django.urls import path

from .views import HomeView, ProductDetailView, ProductListView

app_name = 'products'

urlpatterns = [
	path('', HomeView.as_view(), name='home'),
	path('products/', ProductListView.as_view(), name='list'),
	path('products/<slug:slug>/', ProductDetailView.as_view(), name='detail'),
]