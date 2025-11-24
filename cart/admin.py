from django.contrib import admin

from cart.models import CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    autocomplete_fields = [
        'product',
        'capacity',
    ]


class CartAdmin(admin.ModelAdmin):
    list_display = [
        'user',
    ]
    list_display_links = [
        'user',
    ]
    inlines = [
        CartItemInline,
    ]