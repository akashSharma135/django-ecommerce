from django.shortcuts import redirect, render

from cart.models import CartItem
from order.utils import generate_order_number
from .models import Order
from .forms import OrderForm

def place_order(request, total=0, quantity=0):
    """ places an order """
    current_user = request.user

    # if cart doesn't have any item then redirect to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect(to='store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if not form.is_valid():
            return redirect(to='checkout')

        data = Order()
        data.user= current_user
        data.first_name = current_user.first_name
        data.last_name = current_user.last_name
        data.phone = form.cleaned_data['phone']
        data.email = current_user.email
        data.address_line_1 = form.cleaned_data['address_line_1']
        data.address_line_2 = form.cleaned_data['address_line_2']
        data.country = form.cleaned_data['country']
        data.state = form.cleaned_data['state']
        data.city = form.cleaned_data['city']
        data.pincode = form.cleaned_data['pincode']
        data.order_total = grand_total
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()
        data.order_number = generate_order_number(data=data)
        data.save()

        order = Order.objects.get(user=current_user, is_ordered=False, order_number=data.order_number)

        context = {
            "order": order,
            "cart_items": cart_items,
            "total": total,
            "tax": tax,
            "grand_total": grand_total
        }


        
        return render(request=request, template_name='order/payments.html', context=context)


def payments(request):
    return render(request=request, template_name='order/payments.html')
