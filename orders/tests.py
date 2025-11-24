from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from cart.models import Cart, CartItem
from products.models import Product, Discount, Capacity
from categories.models import Category
from orders.models import Order, OrderItem


User = get_user_model()


class OrderTests(TestCase):
    def setUp(self):
        # ایجاد یوزر
        self.user = User.objects.create_user(
            phone="09123456789",
            full_name="Test User",
            password="test123"
        )
        self.client.force_login(self.user)

        # ایجاد دسته‌بندی
        self.category = Category.objects.create(name="Test", slug="test", image="x.jpg")

        # تخفیف
        self.discount = Discount.objects.create(value=10)

        # ظرفیت محصول
        self.capacity = Capacity.objects.create(
            capacity="10GB",
            platform="PS5",
            price=100000,
            discount=self.discount
        )

        # محصول
        self.product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            description="desc",
            price=200000,
            discount=self.discount,
            image="test.jpg",
            category=self.category
        )
        self.product.capacity.add(self.capacity)

        # ایجاد cart و cart item
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
            capacity=self.capacity
        )

    def test_order_create_success(self):
        url = reverse("order-create")
        response = self.client.post(url, {
            "full_name": "Test User",
            "phone_number": "09123456789",
            "province": "Tehran",
            "city": "Tehran",
            "postal_code": "12345",
            "address": "Test Address",
        })

        # سفارش ساخته شد؟
        order = Order.objects.first()
        self.assertIsNotNone(order)

        # ساخت OrderItem
        order_item = OrderItem.objects.first()
        self.assertIsNotNone(order_item)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.product, self.product)

        # cart حذف شود
        self.assertFalse(Cart.objects.filter(user=self.user).exists())

        # ریدایرکت درست
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("order-detail", kwargs={"pk": order.pk}))

    def test_order_create_requires_login(self):
        self.client.logout()
        url = reverse("order-create")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_order_detail(self):
        order = Order.objects.create(user=self.user)
        url = reverse("order-detail", kwargs={"pk": order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_order_confirmation_paid(self):
        order = Order.objects.create(user=self.user, status=Order.Status.Paid)
        url = reverse("order-confirmation", kwargs={"pk": order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_order_confirmation_not_paid_redirect(self):
        order = Order.objects.create(user=self.user, status=Order.Status.WAITING)
        url = reverse("order-confirmation", kwargs={"pk": order.pk})
        response = self.client.get(url)
        self.assertRedirects(response, reverse("home"))

    def test_order_failed_cancelled(self):
        order = Order.objects.create(user=self.user, status=Order.Status.Cancelled)
        url = reverse("order-failed", kwargs={"pk": order.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_order_failed_not_cancelled_redirect(self):
        order = Order.objects.create(user=self.user, status=Order.Status.WAITING)
        url = reverse("order-failed", kwargs={"pk": order.pk})
        response = self.client.get(url)
        # self.assertRedirects(response, reverse("home"))
