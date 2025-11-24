from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.order_create, name='order-create'),
    path('detail/<int:pk>/', views.order_detail, name='order-detail'),
    path("order-confirmation/<int:pk>/", views.order_confirmation, name="order-confirmation"),
    path("order-failed/<int:pk>/", views.order_failed, name="order-failed"),
]