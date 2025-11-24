from django.contrib.auth import get_user_model
from django.db import models

from products.models import Product, Capacity


class Cart(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='+', null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def cart_org_total(self):
        return sum([item.get_item_org_total() for item in self.items.all()])

    def cart_final_price(self):
        return sum([item.item_final_price() for item in self.items.all()])

    def cart_discount(self):
        return self.cart_org_total() - self.cart_final_price()


    def __str__(self):
        return f"cart: {self.id}"


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='items')
    quantity = models.PositiveIntegerField(default=1)
    capacity = models.ForeignKey(Capacity, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def item_final_price(self):
        if self.capacity:
            return self.capacity.final_price() * self.quantity
        return self.quantity * self.product.get_final_price()

    def get_item_org_total(self):
        if self.capacity:
            return self.capacity.price * self.quantity
        return self.quantity * self.product.price

    def item_discount(self):
        return int(self.get_item_org_total()) - self.item_final_price()
