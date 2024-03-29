from django.shortcuts import render

from store.models import Product


def home(request):
    """
        Home page of the site, shows available products
    """
    products = Product.objects.all().filter(is_available=True)

    context = {
        "products": products
    }

    return render(request=request, template_name='home.html', context=context)