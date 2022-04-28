"""
    models for cart app:
        # Cart
        # CartItem
"""
from django.db import models
from account.models import Account

from store.models import Product, Variation

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.cart_id


class CartItem(models.Model):
    """
        CartItem model contains the items related to a cart of particular user
    """
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    cart = models.ForeignKey(to=Cart, on_delete=models.CASCADE, null=True)
    variations = models.ManyToManyField(to=Variation, blank=True)
    quantity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self) -> int:
        return self.product.price * self.quantity

    def __unicode__(self):
        return self.product
