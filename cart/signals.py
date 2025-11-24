from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart


@receiver(user_logged_in)
def attach_cart_to_user(sender, user, request, **kwargs):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    # سبد مربوط به session (کاربر مهمان)
    try:
        session_cart = Cart.objects.get(session_key=session_key, user=None)
    except Cart.DoesNotExist:
        session_cart = None

    if session_cart:
        # آیا کاربر قبلا سبد داشته؟
        user_cart, created = Cart.objects.get_or_create(user=user)

        # Merge کردن آیتم‌ها
        for item in session_cart.items.all():
            existing_item = user_cart.items.filter(
                product=item.product,
                capacity=item.capacity
            ).first()

            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
            else:
                item.cart = user_cart
                item.save()

        # حذف سبد مهمان
        session_cart.delete()

    # همیشه session_key را پاک می‌کنیم چون سبد به user وصل شد
    request.session['cart_user_id'] = user.id
