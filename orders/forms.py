from django.forms import ModelForm

from orders.models import Order


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = [
            'full_name',
            'phone_number',
            'telegram_id',
            'province',
            'city',
            'postal_code',
            'address',
            'description',
        ]