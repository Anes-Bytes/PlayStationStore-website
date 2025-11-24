from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth import SESSION_KEY

from core.models import OTP

User = get_user_model()


class TestUserModel(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(phone="09121234567", full_name="Test", password="1234")
        self.assertEqual(user.phone, "09121234567")
        self.assertTrue(user.check_password("1234"))
        self.assertFalse(user.is_staff)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(phone="09123334444", password="admin123")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class TestOTP(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("09120000000", password="1234")

    def test_otp_expired(self):
        otp = OTP.objects.create(
            user=self.user,
            code="123456",
            expires_at=timezone.now() - timezone.timedelta(seconds=1)
        )
        self.assertTrue(otp.is_expired())

    def test_otp_not_expired(self):
        otp = OTP.objects.create(
            user=self.user,
            code="123456",
            expires_at=timezone.now() + timezone.timedelta(minutes=1)
        )
        self.assertFalse(otp.is_expired())

