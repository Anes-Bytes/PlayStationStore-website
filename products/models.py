from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import reverse
from categories.models import Category


class ProductManager(models.Manager):
    def active(self):
        return self.get_queryset().filter(is_active=True, status="A")

    def newest(self):
        return self.get_queryset().order_by("-created_at")

    def discounted(self):
        return self.get_queryset().filter(discount__isnull=False)

    def cheapest(self):
        return self.get_queryset().order_by("price")

    def most_expensive(self):
        return self.get_queryset().order_by("-price")


class ProductFeature(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='features')
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)


class Capacity(models.Model):
    capacity = models.CharField(max_length=200)
    platform = models.CharField(max_length=200)
    price = models.IntegerField()
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def final_price(self):
        if not self.discount:
            return self.price
        return max(self.price * (1 - self.discount.value / 100), 0)

    def __str__(self):
        return f"{self.capacity} {self.platform} |{self.price} تومان"


class Product(models.Model):
    class STATUS(models.TextChoices):
        available = 'A', "Available"
        draft = 'D', "draft"
        not_available = 'N', "Not available"

    class Type(models.TextChoices):
        ACCOUNT = 'A', "Account"
        PHYSICAL = 'P', "Physical"
        GIFT_CARD = 'C', "Gift Card"

    type = models.CharField(choices=Type.choices, default=Type.ACCOUNT, max_length=100)
    title = models.CharField(max_length=100)
    slug = models.SlugField(allow_unicode=True)
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    capacity = models.ManyToManyField(Capacity, blank=True)
    price = models.IntegerField()
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    total_sell = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=100, choices=STATUS.choices, default=STATUS.available)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProductManager()

    def __str__(self):
        return self.title

    def get_final_price(self):
        if not self.discount:
            return self.price
        return max(self.price * (1 - self.discount.value / 100), 0)

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})


class Discount(models.Model):
    value = models.IntegerField()

    def __str__(self):
        return f"{self.value}%"


class ProductImages(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')


class Comment(models.Model):
    class STATUS(models.TextChoices):
        approved = 'A', "Approved"
        draft = 'D', "Draft"
        denied = 'N', "Denied"
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    recommend = models.BooleanField(default=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS.choices, default=STATUS.draft)

    def __str__(self):
        return f"{self.user.full_name} | {self.status}"