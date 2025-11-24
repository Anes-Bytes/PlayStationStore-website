from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from categories.models import Category
from products.models import Product
from cart.models import Cart, CartItem

User = get_user_model()


class TestCartViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone="user1", password="pass12345"
        )
        self.category = Category.objects.create(name="category1", slug="category1", image="category1.jpg")

        self.product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            price=200000,
            image="product.jpg",
            category=self.category,
            type=Product.Type.ACCOUNT,
        )

    def test_add_to_cart_authenticated(self):
        self.client.login(username="user1", password="pass12345")

        url = reverse("cart-add", args=[self.product.slug])

        response = self.client.post(url, {"quantity": 2})

        cart = Cart.objects.get(user=self.user)
        item = CartItem.objects.get(cart=cart, product=self.product)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(item.quantity, 2)

    def test_add_to_cart_guest(self):
        url = reverse("cart-add", args=[self.product.slug])

        response = self.client.post(url, {"quantity": 1})

        session_key = self.client.session.session_key
        cart = Cart.objects.get(session_key=session_key)
        item = CartItem.objects.get(cart=cart, product=self.product)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(item.quantity, 1)

    def test_cart_detail_authenticated(self):
        self.client.login(username="user1", password="pass12345")

        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        url = reverse("cart")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.title)

    def test_item_remove(self):
        self.client.login(username="user1", password="pass12345")

        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        url = reverse("cart-remove", args=[item.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(CartItem.objects.filter(id=item.id).exists())
