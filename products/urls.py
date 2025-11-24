from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("products/", views.ProductListView.as_view(), name="products"),
    path("products/<str:slug>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("comment/add/<str:slug>", views.comment_add, name="comment-add"),
]