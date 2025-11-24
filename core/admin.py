from django.contrib import admin

from core.models import SliderBanners, SideBanners, MiddleBanners, SiteSettings, CustomUser, OTP
from products.models import Comment

class UserCommentsInline(admin.TabularInline):
    model = Comment
    extra = 0
    autocomplete_fields = ['user', 'product']


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'phone',
        'full_name',
    ]
    list_display_links = [
        'phone',
        'full_name',
    ]
    search_fields = [
        'id',
        'phone',
        'full_name',
    ]
    ordering = ['created_at']

    inlines = [
        UserCommentsInline,
    ]

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = [
        "user_id",
        "code"
    ]


@admin.register(Comment)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ["user", "status"]
    list_display_links = ["user", "status"]
    search_fields = ["user", "status"]
    ordering = ['-created_at']
    list_filter = [
        "status",
    ]

admin.site.register(SliderBanners)
admin.site.register(SideBanners)
admin.site.register(MiddleBanners)
admin.site.register(SiteSettings)
