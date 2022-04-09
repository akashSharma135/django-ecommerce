from django.shortcuts import render


def cart(request):
    return render(request=request, template_name='cart/cart.html')
