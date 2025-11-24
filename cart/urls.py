from django.urls import path

from  . import views

urlpatterns = [
    path('add/<str:product_slug>', views.add_to_cart, name='cart-add'),
    path('', views.cart_detail, name='cart'),
    path('remove/<int:item_id>', views.item_remove, name='cart-remove'),
    path('delete/', views.cart_delete, name='cart-delete'),
]
