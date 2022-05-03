from django.urls import path

from . import views

urlpatterns = [
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('payment-successful/', views.payment_successful, name='paymnent_successful'),
    path('store-order-details/', views.my_webhook_view, name='my_webhook_view')
]
