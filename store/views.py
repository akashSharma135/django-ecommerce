from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages

from cart.models import CartItem

from .models import Product, ReviewRating
from category.models import Category
from order.models import OrderProduct
from cart.views import cart_id
from .forms import ReviewForm


def store(request, category_slug=None):
    """
        Show all the products available in store or show products of a particular category
    """
    products = None

    # if true show products of particular category else show available products
    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=categories, is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(number=page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
        paged_products = paginator.get_page(number=page)
        product_count = products.count()

    context = {
        "products": paged_products,
        "product_count": product_count
    }

    return render(request=request, template_name='store/store.html', context=context)


def product_detail(request, category_slug, product_slug):
    """
        Show the details of a product
    """
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=cart_id(request=request), product=product).exists()
    except Product.DoesNotExist:
        return HttpResponseNotFound("Not Found")

    order_product = False
    order_product = OrderProduct.objects.filter(user=request.user, product_id=product.id).exists()

    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    context = {
        "product": product,
        "in_cart": in_cart,
        "order_product": order_product,
        "reviews": reviews
    }

    return render(request=request, template_name='store/product-detail.html', context=context)


def search(request):
    keyword = request.GET.get('keyword', None)
    if keyword:
        products = Product.objects.filter(
            Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
        ).order_by('-created_date')
        product_count = products.count()
        
        context = {
            "products": products,
            "product_count": product_count
        }
    return render(request=request, template_name='store/store.html', context=context)

def submit_review(request, product_id):
    if request.method == "POST":
        url = request.META.get('HTTP_REFERER')
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, "Your review is updated!")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if not form.is_valid():
                pass
            data = ReviewRating()
            data.subject = form.cleaned_data['subject']
            data.rating = form.cleaned_data['rating']
            data.review = form.cleaned_data['review']
            data.ip_address = request.META.get('REMOTE_ADDR')
            data.product_id = product_id
            data.user_id = request.user.id
            data.save()
            messages.success(request, "Your review is saved!")
            return redirect(url)
