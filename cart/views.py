from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from .models import Cart, CartItem
from store.models import Product, Variation


def cart_id(request):
    """
        generates new cart_id using the session key
    """
    cart = request.session.session_key

    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    # get the product
    product = Product.objects.get(id=product_id)

    # initializing list for variations of product
    product_variation = []

    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                # get the product variations
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    # get the cart, if does not exists then create it
    
    try:
        cart = Cart.objects.get(
            cart_id=cart_id(request=request)
        )
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id=cart_id(request=request)
        )
        cart.save()
    
    if request.user.is_authenticated:
        try:
            if len(product_variation) > 0:
                for item in product_variation:    
                    cart_item = CartItem.objects.get(user=request.user, product=product, variations=item)
                    # add the product variation to the already existing cart item
                    cart_item.variations.add(item)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product, quantity=1, user=request.user)
            if len(product_variation) > 0:
                for item in product_variation:
                    # add the product variation to the newly created cart item
                    cart_item.variations.add(item)
            cart_item.save()
    else:
        try:
            if len(product_variation) > 0:
                for item in product_variation:    
                    cart_item = CartItem.objects.get(cart=cart, product=product, variations=item)
                    # add the product variation to the already existing cart item
                    cart_item.variations.add(item)
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variation) > 0:
                for item in product_variation:
                    # add the product variation to the newly created cart item
                    cart_item.variations.add(item)
            cart_item.save()
    return redirect(to='cart')


def remove_cart(request, product_id, cart_item_id):
    """
        decreases the quantity of a product
    """
    product = get_object_or_404(klass=Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=cart_id(request=request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect(to='cart')


def remove_cart_item(request, product_id, cart_item_id):
    """
        removes the item from the cart
    """
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')



def cart(request, total=0, quantity=0):
    """
        retrieves the cart details
    """
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=cart_id(request=request))
            cart_items = CartItem.objects.filter(cart=cart)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = tax + total

        context = {
            "total": total,
            "quantity": quantity,
            "cart_items": cart_items,
            "tax": tax,
            "grand_total": grand_total
        }
    except ObjectDoesNotExist:
        context = {
            "total": total,
            "qunatity": quantity
        }

    return render(request=request, template_name='cart/cart.html', context=context)


@login_required(login_url='login')
def checkout(request, total=0, quantity=0):
    """ renders to the checkout page with some prefilled information about user """
    try:
        cart_items = CartItem.objects.filter(user=request.user)
        # calculate tax and total amount
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = tax + total

        context = {
            "total": total,
            "quantity": quantity,
            "cart_items": cart_items,
            "tax": tax,
            "grand_total": grand_total,
            "user": request.user
        }
    except ObjectDoesNotExist:
        context = {
            "total": total,
            "qunatity": quantity
        }
    return render(request=request, template_name='store/checkout.html', context=context)