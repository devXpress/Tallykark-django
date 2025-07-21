from django.contrib import admin
from. models import Payment, Order, OrderProduct

# Register your models here.

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'order_total', 'is_ordered', 'status', 'created_at']
    list_filter = ['status', 'is_ordered', 'created_at']
    search_fields = ['order_number', 'user__email']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'user', 'payment_method', 'amount_paid', 'status', 'created_at']
    list_filter = ['payment_method', 'status']
    search_fields = ['payment_id', 'user__email']

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'color', 'size', 'ordered']
    list_filter = ['ordered']
    search_fields = ['order__order_number', 'product__product_name']

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)

