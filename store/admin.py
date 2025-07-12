from django.contrib import admin
from .models import Product

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ('product_name','price', 'stock','category', 'created_at', 'updated_at', 'is_available')
    list_filter = ('is_available', 'category')
    search_fields = ('product_name', 'category__category_name')
admin.site.register(Product, ProductAdmin)    
