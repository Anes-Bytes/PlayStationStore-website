from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'full_name',
        'status',
    ]
    list_display_links = [
        'id',
        'user',
        'full_name',
    ]
    search_fields = [
        'id'
        'user',
        'full_name',
    ]
    list_filter = [
        'user',
        'status',
    ]
    inlines = [OrderItemInline]
