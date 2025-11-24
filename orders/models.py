from django.db import models
from django.contrib.auth import get_user_model

from products.models import Product, Capacity


class Order(models.Model):
    class Status(models.TextChoices):
        WAITING = "W", "Waiting"
        Paid = "P", "Paid"
        Cancelled = "C", "Cancelled"

    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name="orders")
    full_name = models.CharField(max_length=150, blank=True)

    phone_number = models.CharField(max_length=15, blank=True)
    telegram_id = models.CharField(max_length=15, blank=True)

    province = models.CharField(max_length=15, blank=True)
    city = models.CharField(max_length=15, blank=True)
    postal_code = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=150, blank=True)
    description = models.CharField(max_length=150, blank=True)

    status = models.CharField(max_length=150, choices=Status.choices, default=Status.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def org_price(self):
        return sum([item.org_price for item in self.items.all()])

    def total_discount(self):
        return sum([item.total_discount for item in self.items.all()])

    def final_price(self):
        return sum([item.final_price for item in self.items.all()])

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="+")
    quantity = models.IntegerField(default=1)
    capacity = models.ForeignKey(Capacity, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    final_price = models.PositiveIntegerField()
    org_price = models.PositiveIntegerField()
    total_discount = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product}"
