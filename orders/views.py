from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from cart.models import Cart, CartItem
from orders.forms import OrderForm
from orders.models import Order, OrderItem

@login_required()
def order_create(request):
    if request.user.is_authenticated:
        cart, _ = (Cart.objects.prefetch_related(Prefetch('items', queryset=CartItem.objects.select_related("product", "product__discount").all()))
                   .select_related("user")
                   .get_or_create(user=request.user))
    else:
        if not request.session.session_key:
            request.session.create()

        cart, _ = Cart.objects\
            .prefetch_related(Prefetch('items', queryset=CartItem.objects.select_related("product", "product__discount").all()))\
            .get_or_create(session_key=request.session.session_key)

    form = OrderForm(request.POST)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        if not request.user.full_name:
            request.user.full_name = obj.full_name
        for item in cart.items.all():
            OrderItem.objects.create(
                order=obj,
                product=item.product,
                quantity=item.quantity,
                final_price=item.item_final_price(),
                org_price=item.get_item_org_total(),
                total_discount=item.item_discount(),
                capacity=item.capacity,
            )
        cart.delete()
        messages.success(request, 'سفارش شما آماده پرداخت است')
        return redirect("order-detail", pk=obj.pk)

    messages.error(request, "خطا در دریافت اطلاعات")
    return redirect("home")

@login_required()
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk, user=request.user)
    return render(request, "orders/order-detail.html", {"order": order})

@login_required()
def order_confirmation(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items"), pk=pk, user=request.user)
    if order.status == Order.Status.Paid:
        messages.success(request, "با تشکر از اعتماد شما")
        return render(request, "orders/order-confirmation.html", {"order": order})
    return redirect("home")

@login_required()
def order_failed(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    order.status = Order.Status.Cancelled
    order.save()
    if order.status == Order.Status.Cancelled:
        messages.error(request, "پرداخت ناموفق")
        return render(request, "orders/order-failed.html", {"order": order})
    return redirect("home")

