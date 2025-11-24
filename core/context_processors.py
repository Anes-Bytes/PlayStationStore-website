from .models import SiteSettings

from categories.models import Category
from django.core.cache import cache

def site_settings(request):
    categories = cache.get('categories')
    site_settings = cache.get('site_settings')

    if site_settings is None:
        site_settings = SiteSettings.objects.first()
        cache.set('site_settings', site_settings, 3600)

    if categories is None:
        categories = Category.objects.all()
        cache.set('categories', categories, 3600)

    return {"site_settings": site_settings, "categories": categories}