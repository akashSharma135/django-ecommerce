import stripe
import json

from django.conf import settings
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from cart.models import CartItem
from account.models import Account
from order.models import Order, Payment
from order.utils import generate_order_number

def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_API_KEY

    customer_email = request.user.email
    items = CartItem.objects.filter(user=request.user)

    line_items = []

    # list all the items in cart
    for item in items:
        image_url = request.build_absolute_uri(item.product.images.url)

        line_item_details = {
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.product_name,
                    'images': [image_url]
                },
                'unit_amount': item.product.price * 100
            },
            'quantity': item.quantity,
            'tax_rates': ['txr_1KvPMoCJVR68fF0JJZURRffE'],
        }

        line_items.append(line_item_details)

    # create checkout session
    session = stripe.checkout.Session.create(
        customer_email=customer_email,
        submit_type='pay',
        billing_address_collection='auto',
        payment_method_types=['card'],
        shipping_address_collection={
            'allowed_countries': ['IN'],
        },
        payment_intent_data={
            "metadata": {
                "user_id": request.user.id
            }
        },
        shipping_options=[
            {
                'shipping_rate_data': {
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': 0,
                        'currency': 'usd',
                    },
                    'display_name': 'Free shipping',
                    # Delivers between 5-7 business days
                    'delivery_estimate': {
                        'minimum': {
                            'unit': 'business_day',
                            'value': 5,
                        },
                        'maximum': {
                            'unit': 'business_day',
                            'value': 7,
                        },
                    }
                }
            },
            {
                'shipping_rate_data': {
                    'type': 'fixed_amount',
                    'fixed_amount': {
                        'amount': 50,
                        'currency': 'usd',
                    },
                    'display_name': 'Next day air',
                    # Delivers in exactly 1 business day
                    'delivery_estimate': {
                        'minimum': {
                            'unit': 'business_day',
                            'value': 1,
                        },
                        'maximum': {
                            'unit': 'business_day',
                            'value': 1,
                        },
                    }
                }
            },
        ],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/order/payment-successful'),
        cancel_url=request.build_absolute_uri('/cart')
    )

    return redirect(session.url)


def payment_successful(request):
    return render(request=request, template_name='order/payment-success.html')


@csrf_exempt
def my_webhook_view(request):
    """
        Handle stripe events via webhook
    """
    payload = request.body
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        payment_method = stripe.PaymentMethod.retrieve(
            payment_intent.payment_method
        )
        current_user = Account.objects.get(id=payment_intent.metadata.user_id)
        address = payment_intent.shipping.address
        
        payment = Payment.objects.create(
            user=current_user,
            payment_id=payment_intent.id,
            payment_method=payment_method.type,
            amount_paid=(payment_intent.amount / 100),
            status=payment_intent.status
        )
        
        Order.objects.create(
            user=current_user,
            payment=payment,
            order_number=generate_order_number(data=current_user),
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            # TODO: Add phone field in Account model
            phone="+919810357643",
            email=current_user.email,
            address_line_1=address.line1 if address.line1 else '',
            address_line_2=address.line2 if address.line2 else '',
            country=address.country,
            state=address.city,
            pincode=address.postal_code,
            order_total=payment_intent.amount,
            tax="2",
            status=payment_intent.status,
            ip=request.META.get('REMOTE_ADDR'),
            is_ordered=True
        )
    else:
        # TODO: Need to handle more events
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)
