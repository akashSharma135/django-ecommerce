"""
    Registeration of models on django admin panel
"""
from django.contrib import admin

from .models import Product, Variation

class ProductAdmin(admin.ModelAdmin):
    # create slug on basis of product_name
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')

admin.site.register(
    model_or_iterable=Product,
    admin_class=ProductAdmin
)

admin.site.register(
    model_or_iterable=Variation,
    admin_class=VariationAdmin
)