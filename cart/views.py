from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from cart.forms import AddToCartForm
from cart.models import Cart, CartItem
from products.models import Product


def add_to_cart(request, product_slug):
    form = AddToCartForm(request.POST)
    product = get_object_or_404(Product, slug=product_slug)

    if form.is_valid():
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            if not request.session.session_key:
                request.session.create()
            cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)

        capacity = form.cleaned_data.get('capacity') or None

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            capacity_id=capacity
        )

        if created:
            cart_item.quantity = form.cleaned_data['quantity']
        else:
            cart_item.quantity += form.cleaned_data['quantity']

        cart_item.save()

        messages.success(request, 'محصول با موفقیت به سبد خرید اضافه شد.')

    return redirect("cart")

def cart_detail(request):
    if request.user.is_authenticated:
        cart, _ = (Cart.objects.prefetch_related(Prefetch('items', queryset=CartItem.objects.prefetch_related("capacity").select_related("product").all()))
                   .select_related("user").defer("created_at", "updated_at")
                   .get_or_create(user=request.user))
    else:
        if not request.session.session_key:
            request.session.create()

        cart, _ = Cart.objects\
            .prefetch_related(Prefetch('items', queryset=CartItem.objects.prefetch_related("capacity").select_related("product", "product__discount").defer("created_at", "updated_at")))\
            .get_or_create(session_key=request.session.session_key)

    is_physical = False
    items = cart.items.all()
    for item in items:
        if item.product.type == Product.Type.PHYSICAL:
            is_physical = True
            break



    return render(request, 'cart/cart-detail.html', {'cart': cart, 'is_physical': is_physical})

def item_remove(request, item_id):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart = get_object_or_404(Cart, session_key=request.session.session_key)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect('cart')

def cart_delete(request):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart = get_object_or_404(Cart, session_key=request.session.session_key)

    cart.delete()
    return redirect('cart')