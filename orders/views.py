from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, OrderProduct
import datetime
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def payments(request):
    return render(request, 'orders/payments.html')


def place_order(request, total=0, quantity=0):
    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d')

            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        reference = data.get("reference")
        order_number = data.get("order_number")

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",  # Replace with real key
        }

        response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
        res_data = response.json()

        if res_data['data']['status'] == 'success':
            order = Order.objects.get(order_number=order_number)
            user = order.user

            payment = Payment.objects.create(
                user=user,
                payment_id=res_data['data']['id'],
                payment_method='Paystack',
                amount_paid=res_data['data']['amount'] / 100,
                status='Paid'
            )

            order.payment = payment
            order.is_ordered = True
            order.save()

            cart_items = CartItem.objects.filter(user=user)
            for item in cart_items:
                color = ''
                size = ''
                for v in item.variation.all():
                    if v.variation_category.lower() == 'color':
                        color = v.variation_value
                    elif v.variation_category.lower() == 'size':
                        size = v.variation_value

                order_product = OrderProduct.objects.create(
                    order=order,
                    payment=payment,
                    user=user,
                    product=item.product,
                    quantity=item.quantity,
                    product_price=item.product.price,
                    ordered=True,
                    color=color,
                    size=size,
                    variation=item.variation.first()
                )

                item.product.stock -= item.quantity
                item.product.save()

            cart_items.delete()

            message = render_to_string('orders/payment_email.html', {
                'user': user,
                'amount': payment.amount_paid,
                'order_number': order.order_number,
            })
            send_mail('Order Confirmation - TallyKart', message, settings.EMAIL_HOST_USER, [user.email])

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'fail'})


def payment_success(request):
    order = Order.objects.filter(user=request.user, is_ordered=True).latest('created_at')
    payment = order.payment
    ordered_products = OrderProduct.objects.filter(order=order)

    total = 0
    for item in ordered_products:
        item.line_total = item.product_price * item.quantity
        total += item.line_total

    tax = (2 * total) / 100
    grand_total = total + tax

    context = {
        'order': order,
        'payment': payment,
        'ordered_products': ordered_products,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'full_name': f"{order.first_name} {order.last_name}",
        'full_address': f"{order.address_line_1}, {order.city}, {order.state}, {order.country}",
    }
    return render(request, 'orders/payment_success.html', context)
