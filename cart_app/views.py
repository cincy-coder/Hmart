from django.shortcuts import render,redirect, get_object_or_404
from store.models import *
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from .models import *
from .forms import AddressForm
import random
from django.utils import timezone
import razorpay
from  django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from user.models import *
from django.http import JsonResponse
from .utils import *
import uuid
from django.http import HttpResponseBadRequest
from django.contrib import messages
import json
from django.views.decorators.http import require_POST
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required(login_url="/login")
def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/login")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="/login")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")

def calculate_cart_total(cart):

    total = 0
    for item in cart.values():
        total = total + (item['price'] * item['quantity'])
    return total

def calculate_grand_total(cart_total_amount):
    grand_total=cart_total_amount+(grand_total*.07)+1000
    return grand_total  # Placeholder

@login_required(login_url="/login")
def cart_clear(request):
    cart = request.session.get('cart', {})
    cart.clear()
    request.session['cart'] = cart
    return redirect('product')

@login_required(login_url="/login")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")

@login_required(login_url="/login")
def add_user_coupon(request):
    user = request.user
    if request.method == "POST":
        input_coupon = request.POST.get('input_coupon')
        try:
            coupon = Coupon.objects.get(code=input_coupon, is_active=True, expiry_date__gte=timezone.now().date())
        except Coupon.DoesNotExist:
            # Handle invalid coupon case (e.g., show an error message)
            return redirect("cart_detail")  

        # Check if the user has already redeemed this coupon
        if not UserCoupon.objects.filter(user=user, coupon=coupon).exists():
            UserCoupon.objects.create(user=user, coupon=coupon, redeemed_at=timezone.now())
    
    return redirect("cart_detail")

@login_required
@require_POST
def update_cart_quantity(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    new_quantity = data.get('quantity') 
    
    print(product_id)
    print(new_quantity)
    # Validate input values
    if not product_id or not new_quantity:
        return JsonResponse({'success': False, 'message': 'Invalid data.'})
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product does not exist.'})
    
    # Assume the product has an attribute 'stock' representing available units
    available_stock = product.stock
    
    if new_quantity > available_stock:
        return JsonResponse({
            'success': False, 
            'message': 'Quantity exceeds available stock.',
            'available_stock': available_stock
        })
    
    # Update the cart stored in the session
    cart = request.session.get('cart', {})

    for key, item in cart.items():
        print("1111111111111111111111111111111111111")

        if str(item['product_id']) == str(product_id):
            item['quantity'] =new_quantity
            print(f"Item Quantity: {item['quantity']}")

            # Optionally update available stock
            item['available_stock'] = available_stock
            break

    request.session['cart'] = cart  # Explicitly reassign the modified cart
    request.session.modified = True  # Force session to recognize the change
    print(";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")
    print(request.session['cart'])
        
    # Calculate the new subtotal for this product
    subtotal = product.price * new_quantity
    
    
    
    # Optionally, you could also recalculate total cart values here.
    return JsonResponse({
        'success': True,
        'new_quantity': new_quantity,
        'subtotal': subtotal,
        'available_stock': available_stock,
    })


@login_required(login_url="/login")
def cart_detail(request):
    cart = request.session.get('cart', {})  # Retrieve the cart from the session
    products_info = []
    user = request.user
    coupon_discount = 0
    payment_unique_id="order-"+ str(random.randint(11111111111, 99999999999))
    coupon_display = Coupon.objects.filter(is_active=True)[0]
    discount=0
    total_price = 0  # Initialize the total price variable
    total_discount = 0  # Initialize total discount variable
    user_coupon = UserCoupon.objects.filter(user=user, redeemed_at__isnull=False).first()   
    print("------------------------------user_coupon----------------------------------------")
    print(user_coupon)
    print("----------------------------------------------------------------------------------")
    for key, item in cart.items():
        product_id = item['product_id']
        
        # Fetch product details from the database
        try:
            product = Product.objects.get(id=product_id)
            category = product.categories  # Assuming categories is the FK field name
            
            # Calculate discount for product
            active_offer = product.get_active_offer()
            discount_percentage = active_offer.discount_percentage if active_offer else 0
            print(cart)
            quantity=item['quantity']
            cart_price = int(item['price']) * int(item['quantity'])
            discount_amount = int(cart_price) * int(discount_percentage) *0.01
            final_price = int(cart_price) - int(discount_amount)

            # Add product's final price to the total
            
            print(f"CART PRICE:{cart_price}")
            print(f"Quantity:{item['quantity']}")
            print(f"DISCOUNT_AMOUNT:{discount_amount}")
            total_price += final_price
            print(f"total_price:{total_price} final_price:{final_price}")
            #Calculate category-level discount (if applicable)
            category_discount = category.discount if hasattr(category, 'discount') else 0
            category_discount_amount = (final_price * category_discount) / 100
            total_discount += category_discount_amount

            # Append details
            products_info.append({
                'product_name': item['name'],
                'category': category.name,
                'original_price': cart_price,
                'discount_percentage': discount_percentage,
                'user_coupon': user_coupon,
                'discount_amount': discount_amount,
                'category_discount_percentage': category_discount,
                'category_discount_amount': category_discount_amount,
                'final_price': final_price - category_discount_amount,  # Subtract category discount
            })
            request.session['products_info']=products_info
            print("'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''")
            print(f"products_info:{request.session['products_info']}")
        except Product.DoesNotExist:
            print(f"Product with ID {product_id} not found in the database.")

    # Apply category discount to the total price
    final_total_price = total_price - total_discount

    # Check if coupon code is applied
    coupon_code = UserCoupon.objects.filter(user=user, redeemed_at__date=timezone.now().date()).first()
    

    #user_coupon = UserCoupon.objects.filter(user=user).first()
    #order_data_store=Order_data_store.objects.filter(user=user,order_id=request.session['unique_id'])
    # Calculate grand total after coupon discount
    grand_total = final_total_price + 1000  # Add shipping charge (fixed at 1000)
    gst_amount = grand_total * 0.07  # GST is 7% of the grand total
    grand_total += gst_amount  # Add GST to the grand total
    
    # Print details in terminal for debugging
    for product in products_info:
        print(f"Product: {product['product_name']}")
        print(f"Category: {product['category']}")
        print(f"Original Price: {product['original_price']}")
        print(f"Discount: {product['discount_percentage']}%")
        print(f"Discount Amount: {product['discount_amount']}")
        print(f"Category Discount: {product['category_discount_percentage']}%")
        print(f"Category Discount Amount: {product['category_discount_amount']}")
        print(f"Final Price: {product['final_price']}")
        discount=product['discount_percentage']
        
    coupon=Coupon.objects.filter(is_active=True).first()
    print(f"Coupon:{coupon}")
    print(total_price)
    print(f"grand_total: {grand_total}")
    print(f"Discount : {discount}")
    
    request.session['total_amt_checkout'] = total_price
    request.session['paid_amt_checkout'] = int(grand_total)
    request.session['payment_unique_id'] = payment_unique_id
    request.session['discount_percentage_product'] = discount
    request.session['coupon_used'] = False
    
    if coupon_code:
        grand_total= grand_total-(grand_total*coupon.discount_amount/100)
        request.session['paid_amt_checkout'] = int(grand_total)
        request.session['coupon_used'] = True
    print(request.session['payment_unique_id'])
    print(f"Coupon discount: {coupon_discount}")

    # Render the cart details template with the calculated data
    return render(request, 'cart/cart_details.html', {
        'products_info': products_info,
        'total_price': total_price,
        'total_discount': total_discount,
        'final_total_price': final_total_price,
        'coupon_code': coupon_code,
        'coupon_discount': coupon_discount,
        'grand_total': grand_total,
        'gst_amount': gst_amount,
        'user_coupon': user_coupon,
        'coupon_display':coupon_display,
        'calculate_grand_total': calculate_grand_total
    })
    
@login_required(login_url="/login")
def check_out(request): 
    return render(request, 'cart/checkout.html')

@login_required(login_url="/login")
def address_list(request):
    addresses = Address.objects.filter(user=request.user)  # Get all addresses
    wallet = Wallet.objects.filter(user=request.user).first()
    
    # Calculate the amount to be paid after using the wallet
    total_checkout_amt = request.session.get('paid_amt_checkout', 0)
    
    if wallet:
        Amount_to_be_paid = total_checkout_amt - wallet.balance
        if Amount_to_be_paid < 0:
            Amount_to_be_paid = 0  
        wallet_refund = total_checkout_amt - Amount_to_be_paid
    else:
        Amount_to_be_paid = total_checkout_amt
        wallet_refund = 0

    # If the amount to be paid is 0, mark the order as paid
    order_status = "Pending"
    if Amount_to_be_paid == 0:
        order_status = "Paid"
    
    order=Order.objects.filter(payment_id=request.session.get('payment_unique_id'))
    if order:
        order.update(status=order_status)
        order.save()
    order_data_store = Order_data_store.objects.create(
        user=request.user,
        order_id=request.session.get('payment_unique_id'),
        total_amt=request.session.get('total_amt_checkout'),
        paid_amt=total_checkout_amt,
        discount_percentage=request.session.get('discount_percentage_product'),
        coupon_used=request.session.get('coupon_used')
    )
    order_data_store.save()

    context = {
        'addresses': addresses,
        'wallet': wallet,
        'amount_to_be_paid': Amount_to_be_paid,
        'wallet_refund': wallet_refund
    }
    return render(request, 'cart/checkout.html', context)

@login_required(login_url="/login")
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('address_list')
    else:
        form = AddressForm()
    return render(request, 'cart/address_form.html', {'form': form})
    #return render(request, 'cart/checkout.html', {'form': form})

@login_required(login_url="/login")
def edit_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'cart/address_form.html', {'form': form})

@login_required(login_url="/login")
def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('address_list')
    return render(request, 'cart/address_confirm_delete.html', {'address': address})



@csrf_exempt
def cod_place_order(request):
    
    if request.method == 'POST':
        cart= request.session.get('cart')
        user=request.user
        id=request.POST.get('selected_address')
        address=get_object_or_404(Address, pk=id, user=user)
        amt= request.POST.get('amount')
        print("[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[[00000000000000]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]")
        print(request.POST.get('payment-method'))
        if request.POST.get('payment-mode') == "cash-on-delivery":
            order=Order.objects.create(
                user=user,
                address=address,
                amount=amt,
                payment_id=request.session.get('payment_unique_id'),
                paid = False,
                payment_mode="cash-on-delivery"
            )
            order.save()
           
        
        else:
            order=Order.objects.create(
                user=user,
                address=address,
                amount=amt,
                payment_id=request.session.get('payment_unique_id'),
                paid = True,
                payment_mode="buy-now"
            )
            order.save()
            
        for i in cart:
            a=int(cart[i]['price'])
            b=cart[i]['quantity']
            gst=.07
            total=(a*b*gst)+(a*b)+1000
            
            product=Product.objects.filter(id=cart[i]['product_id'])
            stock=product[0].stock-int(cart[i]['quantity'])
            product.update(stock=stock)
            if stock==0:
                product.update(status='Draft')
            print(stock)

            order_item = Order_item(
                order=order,
                product=cart[i]['name'],
                image=cart[i]['image'],
                quantity=cart[i]['quantity'],
                price=int(cart[i]['price']) * int(cart[i]['quantity']),
                total=request.POST.get('amount')
            )
            order_item.save()  
        return redirect('thanku')
    return render(request, 'cart/thanku.html')

@csrf_exempt
def razor_place_order(request):
    context={
        "user": request.user,
        "address":request.POST.get('select_address'),
        'amount':request.POST.get('amount'),
            }
    return render(request, 'cart/razor_placeorder.html',context)   

    
    

@csrf_exempt
def place_order(request):      
    payment=client.order.create({
                'amount':500,
                'currency':"INR",
                'payment_capture':'1',
            })
    
    order_id=request.session.get('payement_unique_id')
    
    print(order_id)
    if request.method == 'POST':
        cart= request.session.get('cart')
        user=request.user
        id=request.POST.get('selected_address')
        address=get_object_or_404(Address, pk=id, user=user)
        amt= request.session['paid_amt_checkout']
        payment=request.POST.get('payment')
        wallet_refund=request.POST.get('wallet_refund')
        
        wallet = get_object_or_404(Wallet, user=request.user)
        wallet.balance = float(wallet.balance)-float(wallet_refund)
        wallet.save()
        
        payment_id=order_id
        context={
                "address":id,
                "order_id":payment_id,
                'amount': amt,
                'payment': payment,
                'payment_mode':request.POST.get('payment-method')
                    }
        context_razor={
                    "address" : id,                   
                    'amount': 500,
                    
                        }
        
        if request.POST.get('payment-method')=="cash-on-delivery" or request.POST.get('payment-method')=="buynow":
            return render(request, 'cart/cod_placeorder.html',context)
        
        
    
        elif request.POST.get('payment-method')=="razorpay":
            order=Order.objects.create(
            user=user,
            address=address,
            amount=request.POST.get('amount'),
            payment_id=request.session.get('payment_unique_id'),
            payment_mode="razorpay",
            paid=True,
                )
            
            order.save()
            for i in cart:            
                product=Product.objects.filter(id=cart[i]['product_id'])
                stock=product[0].stock-int(cart[i]['quantity'])
                product.update(stock=stock)
                if stock==0:
                    product.update(status='Draft')
                print(stock)
                
                order_item = Order_item(
                    order=order,
                    product=cart[i]['name'],
                    image=cart[i]['image'],
                    quantity=cart[i]['quantity'],
                    price=int(cart[i]['price'])* int(cart[i]['quantity']),
                    total=request.POST.get('amount')
                )
                order_item.save()
            return render(request, 'cart/razor_placeorder.html',context_razor)  
        else:
            return render(request, 'cart/cod_placeorder.html',context) 
    return render(request, 'cart/thanku.html',context)


@login_required(login_url="/login")
def clear_session(request):
    del request.session['cart']
    #del request.session['payment_unique_id']
    #del request.session['total_amt_checkout']
    #del request.session['paid_amt_checkout']
    return redirect('home')

@login_required(login_url="/login")
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'cart/order_list.html', {'orders': orders})



@login_required(login_url="/login")
def add_to_wishlist(request, product_id):
    """Add a product to the user's wishlist."""
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    wishlist_items = Wishlist.objects.filter(user=request.user).all()
    context = {'wishlist_items': wishlist_items}
    return render(request, 'cart/wishlist_view.html',context)

@login_required(login_url="/login")
def remove_from_wishlist(request, product_id):
    """Remove a product from the user's wishlist."""
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
    
    if wishlist_item.exists():
        wishlist_item.delete()
        
    
    return render(request, 'cart/wishlist_view.html')

@login_required(login_url="/login")
def wishlist_view(request):
    """Display all products in the user's wishlist."""
    product=Product.objects.all()
    wishlist_items = Wishlist.objects.filter(user=request.user).all()
    context = {'wishlist_items': wishlist_items}
    
    return render(request, 'cart/wishlist_view.html', context)

@csrf_exempt
def thanku(request):
    return render(request, 'cart/thanku.html')

@csrf_exempt
def payment_failure(request):
    order = Order.objects.filter(user=request.user,payment_id=request.session.get('payment_unique_id')).first()
    order_data_store=Order_data_store.objects.filter(order_id=request.session.get('payment_unique_id')).first()
    wallet=Wallet.objects.filter(user=request.user).first()
    if order:
        order.paid = False
        order.status = "Payment Failed"
        order.save()
        
        order_data_store.coupon_used = False 
        order_data_store.save()
        wallet.balance = float(wallet.balance)+float(request.session['paid_amt_checkout'])
        wallet.save()
        del request.session['cart']
        return redirect('address_list')
    return render(request, 'cart/payment_failed.html')


@csrf_exempt
def handle_payment(request):

    return render(request,'cart/handle_payment.html')


