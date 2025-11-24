from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, phone, full_name=None, password=None):
        if not phone:
            raise ValueError('Phone is required')

        user = self.model(
            phone=phone,
            full_name=full_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, full_name="Admin", password=None):
        user = self.create_user(
            phone=phone,
            full_name=full_name,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=11, unique=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    def __str__(self):
        return self.phone


class OTP(models.Model):
    user = models.ForeignKey("core.CustomUser", on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.phone} - {self.code}"






class BaseBanners(models.Model):
    image = models.ImageField(upload_to='images/')
    link = models.URLField()

    def __str__(self):
        return self.link

class SliderBanners(BaseBanners):
    pass


class SideBanners(BaseBanners):
    pass


class MiddleBanners(BaseBanners):
    pass


class SiteSettings(models.Model):
    footer_contact_text = models.CharField(max_length=155, blank=True)
    footer_contact = models.CharField(max_length=55, blank=True)
    footer_contact_link = models.CharField(max_length=155, blank=True)

    developer_tag = models.CharField(max_length=155, blank=True)
    developer_link = models.URLField(max_length=155, blank=True)

    telegram = models.URLField(max_length=100, blank=True)
    instagram = models.URLField(max_length=100, blank=True)
    github = models.URLField(max_length=100, blank=True)

    def __str__(self):
        return self.developer_tag