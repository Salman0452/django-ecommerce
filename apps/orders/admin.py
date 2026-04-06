from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('product', 'quantity', 'unit_price')
    readonly_fields = ('unit_price',)
    extra = 0

    def unit_price(self, obj):
        return obj.price


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'created_at')
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_email', 'product', 'quantity', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('cart__user__email', 'product__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Item Info', {
            'fields': ('cart', 'product', 'quantity')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_email(self, obj):
        return obj.cart.user.email

    get_user_email.short_description = 'User Email'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at', 'is_cancellable')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'

