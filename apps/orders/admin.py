from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'shipping_address')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Order Info', {
            'fields': ('user', 'status', 'total_price')
        }),
        ('Shipping', {
            'fields': ('shipping_address',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )
