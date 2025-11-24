from django import forms

from cart.models import Cart


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1)
    capacity = forms.IntegerField(min_value=1, required=False)
