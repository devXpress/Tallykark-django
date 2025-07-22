from django.contrib import admin
from .models import Product, Variation, ReviewRating

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ('product_name','price', 'stock','category', 'created_at', 'updated_at', 'is_available')
    list_filter = ('is_available', 'category')
    search_fields = ('product_name', 'category__category_name')


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active', 'created_at')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value')


admin.site.register(Product, ProductAdmin)    
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating)