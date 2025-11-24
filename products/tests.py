from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from products.models import Product, Discount, Capacity, ProductFeature, Comment
from categories.models import Category
from django.contrib.auth import get_user_model

User = get_user_model()


class TestProductModels(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Cat1", slug="cat1")

        self.discount = Discount.objects.create(value=20)

        self.product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            price=100000,
            discount=self.discount,
            category=self.category,
            image="products/test.jpg",
            description="desc",
        )

        self.capacity = Capacity.objects.create(
            capacity="10GB",
            platform="PS5",
            price=200000,
            discount=self.discount
        )

    def test_product_final_price(self):
        # 20% off → 80,000
        self.assertEqual(self.product.get_final_price(), 80000)

    def test_capacity_final_price(self):
        # 200000 - 20% = 160000
        self.assertEqual(self.capacity.final_price(), 160000)

    def test_product_manager_active(self):
        active_products = Product.objects.active()
        self.assertIn(self.product, active_products)

    def test_product_manager_discounted(self):
        products = Product.objects.discounted()
        self.assertIn(self.product, products)

    def test_product_absolute_url(self):
        url = self.product.get_absolute_url()
        self.assertEqual(url, reverse("product-detail", kwargs={"slug": "test-product"}))


class TestProductListView(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cat1", slug="cat1")
        self.discount = Discount.objects.create(value=10)

        self.product1 = Product.objects.create(
            title="Game One",
            slug="game-one",
            price=100,
            total_sell=5,
            category=self.category,
            discount=self.discount,
            image="x.jpg",
            description="AAA game"
        )

        self.product2 = Product.objects.create(
            title="Cheap Game",
            slug="cheap",
            price=50,
            category=self.category,
            image="x.jpg",
            description="cheap product"
        )

    def get(self, url):
        return self.client.get(reverse("products") + url)

    def test_list_view_status(self):
        response = self.client.get(reverse("products"))
        self.assertEqual(response.status_code, 200)

    def test_filter_by_category(self):
        response = self.get("?category=cat1")
        self.assertEqual(len(response.context["object_list"]), 2)

    def test_filter_by_price(self):
        response = self.get("?min_price=60&max_price=200")
        self.assertIn(self.product1, response.context["object_list"])
        self.assertNotIn(self.product2, response.context["object_list"])

    def test_sort_cheapest(self):
        response = self.get("?sort_query=cheapest")
        products = list(response.context["object_list"])
        self.assertEqual(products[0], self.product2)  # 50

    def test_sort_expensive(self):
        response = self.get("?sort_query=most-expensive")
        products = list(response.context["object_list"])
        self.assertEqual(products[0], self.product1)

    def test_search(self):
        response = self.get("?q=AAA")
        self.assertIn(self.product1, response.context["object_list"])
        self.assertNotIn(self.product2, response.context["object_list"])


class TestProductDetailView(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cat1", slug="cat1")
        self.product = Product.objects.create(
            title="Test Product",
            slug="test-product",
            price=100,
            category=self.category,
            image="x.jpg",
            description="demo",
        )

    def test_detail_view(self):
        url = reverse("product-detail", kwargs={"slug": "test-product"})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["product"], self.product)


class TestHomeView(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cat1", slug="cat1", image="x.jpg")
        Product.objects.create(
            title="P1",
            slug="p1",
            price=10,
            category=self.category,
            image="x.jpg",
            description="test",
        )

    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("newest_products", response.context)
        self.assertIn("categories", response.context)


class TestCommentAdd(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(phone="09120000000", password="1234")

        self.category = Category.objects.create(name="Cat1", slug="cat1", image="x.jpg")
        self.product = Product.objects.create(
            title="P1",
            slug="p1",
            price=10,
            category=self.category,
            image="x.jpg",
            description="test",
        )

    def test_add_comment_logged_in(self):
        self.client.login(phone="09120000000", password="1234")

        url = reverse("comment-add", kwargs={"slug": "p1"})
        response = self.client.post(url, {
            "name": "Test",
            "recommend": True,
            "content": "Good!"
        })

        comments = Comment.objects.filter(product=self.product)
        self.assertEqual(comments.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_add_comment_not_logged_in(self):
        url = reverse("comment-add", kwargs={"slug": "p1"})
        response = self.client.post(url, {
            "name": "Test",
            "recommend": True,
            "content": "Good!"
        })

        # چون user نداره -> فرم نامعتبر → پیام خطا → کامنت ساخته نمی‌شود
        comments = Comment.objects.filter(product=self.product).count()
        self.assertEqual(comments, 0)
        self.assertEqual(response.status_code, 302)
