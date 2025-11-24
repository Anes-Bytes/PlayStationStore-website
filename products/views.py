from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib import messages

from .forms import CommentForm
from .models import Product, Comment, Discount
from core.models import SliderBanners, SideBanners, MiddleBanners
from categories.models import Category
from django.db.models import Q
from django.core.cache import cache


def home_view(request):

    # ======== محصولات جدید ========
    newest_products = cache.get("home_newest_products")
    if newest_products is None:
        newest_products = list(
            Product.objects.newest().select_related("discount")[:15]
        )
        cache.set("home_newest_products", newest_products, 300)

    # ======== محصولات تخفیف دار ========
    discounted_products = cache.get("home_discounted_products")
    if discounted_products is None:
        discounted_products = list(
            Product.objects.discounted().select_related("discount")[:15]
        )
        cache.set("home_discounted_products", discounted_products, 300)

    # ======== محصولات فیزیکی ========
    physical_products = cache.get("home_physical_products")
    if physical_products is None:
        physical_products = list(
            Product.objects.filter(type=Product.Type.PHYSICAL)
            .select_related("discount")[:15]
        )
        cache.set("home_physical_products", physical_products, 300)

    # ======== گیفت کارت ها ========
    gift_cards = cache.get("home_gift_cards")
    if gift_cards is None:
        gift_cards = list(
            Product.objects.filter(type=Product.Type.GIFT_CARD)
            .select_related("discount")[:15]
        )
        cache.set("home_gift_cards", gift_cards, 300)

    # ======== اسلایدر ========
    slider_banners = cache.get("home_slider_banners")
    if slider_banners is None:
        slider_banners = list(SliderBanners.objects.all()[:5])
        cache.set("home_slider_banners", slider_banners, 3600)

    # ======== بنرهای کنار ========
    side_banners = cache.get("home_side_banners")
    if side_banners is None:
        side_banners = list(SideBanners.objects.all()[:2])
        cache.set("home_side_banners", side_banners, 3600)

    # ======== بنرهای وسط ========
    middle_banners = cache.get("home_middle_banners")
    if middle_banners is None:
        middle_banners = list(MiddleBanners.objects.all()[:2])
        cache.set("home_middle_banners", middle_banners, 3600)

    # ======== دسته‌بندی‌ها ========
    categories = cache.get("home_categories")
    if categories is None:
        categories = list(Category.objects.all()[:6])
        cache.set("home_categories", categories, 600)

    # ======== خروجی ========
    return render(request, 'products/home.html', {
        'newest_products': newest_products,
        'discounted_products': discounted_products,
        'physical_products': physical_products,
        'gift_cards': gift_cards,
        'slider_banners': slider_banners,
        'side_banners': side_banners,
        'middle_banners': middle_banners,
        'categories': categories,
    })

class ProductListView(generic.ListView):
    model = Product
    paginate_by = 30
    template_name = 'products/product_list.html'


    def get_queryset(self):
        base_qs = cache.get("active_products_base")
        if base_qs is None:
            base_qs = Product.objects.active()
            cache.set("active_products_base", base_qs, 300)
        queryset = base_qs

        category_slug = self.request.GET.get('category_slug', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        min_price = self.request.GET.get('min_price', None)
        max_price = self.request.GET.get('max_price', None)
        if min_price and max_price:
            queryset = queryset.filter(price__gte=min_price, price__lte=max_price)
        available = self.request.GET.get('available', None)
        if available:
            queryset = queryset.filter(status=Product.STATUS.available)
        special = self.request.GET.get('special', None)
        if special:
            queryset = queryset.filter(discount__isnull=False)

        sort_query = self.request.GET.get('sort_query', None)
        sort_query_map = {
            'newest': lambda: Product.objects.newest(),
            'best-sell': lambda: Product.objects.active().order_by('total_sell'),
            'most-expensive': lambda: Product.objects.most_expensive(),
            'cheapest': lambda: Product.objects.cheapest(),
            'discounted': lambda: Product.objects.discounted(),
        }
        if sort_query in sort_query_map:
            queryset = sort_query_map[sort_query]()
        search = self.request.GET.get('q', None)
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(image__isnull=False)
        context["search_form"] = True
        return context



class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'



    def get_queryset(self):
        return (
            Product.objects
            .prefetch_related('images', 'capacity', 'features')
        )

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(category=context['product'].category).exclude(slug=context['product'].slug)
        context['comments'] = Comment.objects.filter(product=context['product'], status=Comment.STATUS.approved)
        context['comment_form'] = CommentForm()
        return context


@login_required
def comment_add(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = product
            comment.user = request.user
            comment.save()
            messages.success(request, 'کامنت شما ارسال شد و پس از تایید ادمین منتشر میشود.')
            return redirect("product-detail", slug=product.slug)
    messages.error(request, "خطا در ارسال کامنت")
    return redirect("product-detail", slug=product.slug)
