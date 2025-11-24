from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import CustomUser, OTP
from django.utils import timezone
import datetime
import random
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from melipayamak import Api
from orders.models import Order

from environs import Env
env = Env()
env.read_env()

def send_sms(phone, code):
    username = env("MELIPAYAMAK_USERNAME")
    password = env("MELIPAYAMAK_APIKEY")
    api = Api(username, password)
    sms = api.sms()
    to = phone
    _from = env("MELIPAYAMAK_NUMBER")
    text = f'''کد تایید پرشین گیمز

    کد شما: {code}

    توجه: این کد محرمانه است. آن را به هیچ‌کس حتی در صورت ادعای پشتیبانی ندهید.

    پرشین گیمز
    لغو 11'''

    response = sms.send(to, _from, text)

def request_otp(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        full_name = request.POST.get("full_name")
        next_page = request.POST.get("next")

        if next_page:
            request.session["next"] = next_page
        if not phone:
            messages.error(request, "شماره تلفن وارد نشده")
            return redirect("request_otp")

        user, created = CustomUser.objects.get_or_create(phone=phone, defaults={"full_name": full_name})

        code = str(random.randint(100000, 999999))
        OTP.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + datetime.timedelta(minutes=2)
        )
        request.session["phone"] = phone
        send_sms(phone, code)
        messages.success(request, "کد تایید ارسال شد")
        return redirect("verify_otp")

    return redirect("login")

def verify_otp(request):
    if request.method == "POST":
        phone = request.session.get("phone")
        code = request.POST.get("code")
        next_page = request.session.get("next")  # از session می‌خوانیم

        try:
            user = CustomUser.objects.get(phone=phone)
            otp = user.otps.filter(code=code).last()

            if not otp:
                messages.error(request, "کد اشتباه است")
                return redirect("verify_otp")

            if otp.is_expired():
                messages.error(request, "کد منقضی شده")
                return redirect("request_otp")

            login(request, user)
            messages.success(request, "وارد شدید!")

            # اگر next تنظیم شده بود → همانجا برو
            if next_page:
                del request.session["next"]  # فقط یک بار مصرف
                return redirect(next_page)

            # اگر نبود → صفحه اصلی
            return redirect("home")

        except CustomUser.DoesNotExist:
            messages.error(request, "کاربر وجود ندارد")
            return redirect("request_otp")

    return render(request, "core/verify.html")

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    next_page = request.GET.get("next", "")
    return render(request, "core/login.html", {"next": next_page})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    return render(request, "core/signup.html")

def logout_view(request):
    logout(request)
    messages.success(request, "خارج شدید")
    return redirect("home")

@login_required()
def dashboard_view(request):
    user_orders = Order.objects.prefetch_related("items").filter(user=request.user)
    return render(request, "core/profile.html", {'orders': user_orders})

def contact_us_view(request):
    return render(request, "core/contact.html")

def about_us_view(request):
    return render(request, "core/about.html")

def faqs_view(request):
    return render(request, "core/faqs.html")