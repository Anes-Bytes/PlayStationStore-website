from django.urls import path
from . import views

urlpatterns = [
    path("request-otp/", views.request_otp, name="request_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("contact/", views.contact_us_view, name="contact"),
    path("about/", views.about_us_view, name="about"),
    path('faqs/', views.faqs_view, name="faqs"),
]
