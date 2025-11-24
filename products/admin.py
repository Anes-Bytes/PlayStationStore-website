from django.contrib import admin

from django.contrib import admin
from .models import Product, Capacity, Discount, ProductImages, ProductFeature


class ImageInline(admin.TabularInline):
    model = ProductImages
    extra = 0
    autocomplete_fields = ['product']


class FeaturedProductInline(admin.StackedInline):
    model = ProductFeature
    extra = 0
    autocomplete_fields = ['product']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "id")
    list_display_links = ("title",)
    search_fields = ("title", "description")
    list_filter = ("category", "capacity")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-created_at",)

    inlines = [ImageInline, FeaturedProductInline]

admin.site.register(Capacity)
admin.site.register(Discount)