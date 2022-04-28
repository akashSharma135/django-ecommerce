from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from django.core.paginator import Paginator

from cart.models import CartItem

from .models import Product
from category.models import Category
from cart.views import cart_id


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

    context = {
        "product": product,
        "in_cart": in_cart
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
