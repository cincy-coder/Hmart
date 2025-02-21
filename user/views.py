from django.shortcuts import render,redirect, get_object_or_404
from store.models import *
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
import random
from django.utils.timezone import now
from django.http import JsonResponse
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum
from cart_app.models import *
from cart_app.utils import *
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.template.loader import get_template
from .models import *
from .forms import ProfileForm
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import update_session_auth_hash
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import datetime
from datetime import datetime
from django.contrib.sessions.models import Session


# Create your views here.
def BASE(request):
    
    wishlist_items = Wishlist.objects.filter(user=request.user).all()
    
    context = {
        #'wallet': wallet,
        #'wallet_balance': wallet_balance,
        'wishlist_items': wishlist_items,
        
        
            }
    return render(request,'main/base.html',context)


def HOME(request):

    # Fetch published and new products
    product = Product.objects.filter(status='Publish', condition='New')
    

    # Fetch active coupons that have not expired
    available_coupons = Coupon.objects.filter(is_active=True, expiry_date__gte=now().date())
    


    if request.user.is_authenticated:
        # Get IDs of coupons already redeemed by the logged-in user
        redeemed_coupon_ids = UserCoupon.objects.filter(user=request.user).values_list('coupon_id', flat=True)
        wishlist_items = Wishlist.objects.filter(user=request.user).all()
        wallet=Wallet.objects.filter(user=request.user).first()
        #wallet_balance=int(wallet.balance) * 0.0002
        # Exclude redeemed coupons from available coupons
        available_coupons = available_coupons.exclude(id__in=redeemed_coupon_ids)

        # Debugging output (optional, for development)
        print('**************************************************************')
        print(f"Available coupons for user: {available_coupons}")
        #print('Total Wallet Balance:', wallet_balance)
        print('**************************************************************')
        # Context for rendering the template
        context = {
            'product': product,
            'available_coupons': available_coupons,
            'wishlist_items': wishlist_items,
            #'wallet_balance': int(wallet_balance),
        }
    
    else:
        context = {'product': product, 'available_coupons': available_coupons,}
    # Render the homepage template
    return render(request, 'main/index.html', context)

@login_required
def ADMIN_HOME(request):
    """
    Admin dashboard view showing various metrics and charts.
    Includes user counts, sales data, and filtered analytics based on date range.
    """
    
    def get_date_range():
        """Helper function to get and validate date range from request"""
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if not start_date or not end_date:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            
        return start_date, end_date

    def get_sales_metrics(date_range):
        """Helper function to calculate sales metrics within date range"""
        start_date, end_date = date_range
        filtered_orders = Order.objects.filter(date__range=[start_date, end_date])
        
        return {
    'best_selling_products': Order_item.objects.filter(order__in=filtered_orders)
        .values("product")  
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")[:10],

    'best_selling_categories': Order_item.objects.filter(order__in=filtered_orders)
        .values("product")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")[:10],

    'best_selling_brands': Order_item.objects.filter(order__in=filtered_orders)
        .values("product") 
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")[:10]
}

    # Get basic metrics
    user_count = User.objects.count()
    total_amount = Order_data_store.objects.aggregate(Sum('paid_amt'))
    total_amount_value = total_amount['paid_amt__sum'] or 0

    # Get orders and order items
    orders = Order.objects.all()
    recent_order_items = Order_item.objects.filter(order__in=orders)[:10]

    # Get date-filtered metrics
    date_range = get_date_range()
    sales_metrics = get_sales_metrics(date_range)
    
    #total_visitors = Session.objects.count()  # Count active sessions
    product_count = Product.objects.count()
    context = {
        'user_count': user_count,
        'total_amount': total_amount_value,
        'orders': orders,
        'order_items': recent_order_items,
        'users': User.objects.all(),
        'best_selling_products': sales_metrics['best_selling_products'],
        'best_selling_categories': sales_metrics['best_selling_categories'],
        'best_selling_brands': sales_metrics['best_selling_brands'],
        'start_date': date_range[0],
        'end_date': date_range[1],
        #'total_visitors': total_visitors,
        'product_count':product_count
    }

    return render(request, 'admin_temp/admin_index.html', context)


def HandleRegister(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        
        # Check for duplicate username
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        # Check for duplicate email   
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')

        # Check if passwords match
        elif pass1 != pass2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        else:
        # Create and save the user
            user = User.objects.create_user(
            email=email,
            username=username,
            password=pass1,
            first_name=first_name,
            last_name=last_name
        )
        user.save()
        wallet=Wallet.objects.create(
            user=user,
            balance=0
        )
        wallet.save()
        messages.success(request, 'Registration successful! You can now log in.')
        return redirect('login')  # Redirect to the login page after successful registration
    return render(request, 'registration/auth.html')


User = get_user_model()

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    print("------------------------Wallet creation------------------------------")
    if created:
        wallet=Wallet.objects.create(user=instance,balance=0)
        wallet.save()
        print(wallet)


def HandleLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if ((user is not None) and (user.is_staff==False) and (user.is_active==True)) :
            # Log in the user
            login(request, user)
            #messages.success(request, 'Logged in successfully!')
            return redirect('home')  # Replace 'home' with your desired URL name
        elif((user is not None) and (user.is_staff==True) and (user.is_active==True)):
            # Log in the user
            login(request, user)
            #messages.success(request, 'Logged in successfully!')
            return redirect('admin_home')  # Replace 'home' with your desired URL name
        else:
            # Authentication failed
            messages.error(request, 'Invalid username or password.')
            #return redirect('login')  # Replace 'login' with your login URL name
    # Render the login form
    return render(request, 'registration/auth.html')
    
    
    
    
def HandleLogout(request):
    logout(request)
    #messages.success(request, 'You have successfully logged out.')
    return redirect('login')


def forget_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            otp = str(random.randint(100000, 999999))
            # Save OTP in database
            PasswordReset.objects.create(user=user, otp=otp)
            send_mail(
                'Your OTP for Password Reset',
                f'Use this OTP to reset your password: {otp}',
                'cincygreejith@gmail.com',
                [email],
                fail_silently=False,
            )
            # Store email in session for OTP verification
            request.session['reset_email'] = email
            return redirect("verify_otp")
        except User.DoesNotExist:
            return JsonResponse({"error": "User with this email does not exist."})
    return render(request, "registration/forget_password.html")


def verify_otp(request):
    if request.method == "POST":
        email = request.session.get('reset_email')  # Retrieve email from session
        otp = request.POST.get("otp")
        new_password = request.POST.get("new_password")

        if not email:
            return JsonResponse({"error": "Session expired. Please try again."})

        try:
            user = User.objects.get(email=email)
            password_reset = PasswordReset.objects.filter(user=user, otp=otp).first()

            if password_reset and str(password_reset.otp) == str(otp):
                user.set_password(new_password)  # Correctly set the new password
                user.save()
                password_reset.delete()  # Clean up after use
                del request.session['reset_email']  # Clear the session
                return redirect('login')
            else:
                return JsonResponse({"error": "Invalid OTP or OTP expired."})
        except User.DoesNotExist:
            return JsonResponse({"error": "User with this email does not exist."})
    return render(request, "registration/verify_otp.html")


def success(request):
    return render(request,'registration/success.html')



@login_required(login_url='login')
def profile_view(request):   
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None

    addresses = Address.objects.filter(user=request.user) # Get the first address or None
    order = Order.objects.prefetch_related('order_item_set').filter(user=request.user).order_by('-id')
    wallet=Wallet.objects.filter(user=request.user).first()
    
    
    context = {
        'profile': profile,
        'addresses': addresses,
        'order': order,
        'wallet':wallet,
        
    }

    return render(request, 'registration/profile.html', context)


@login_required(login_url='login')
def add_edit_profile(request):
    # Get the user's profile if it exists
    profile = Profile.objects.filter(user=request.user).first()
    
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user  # Associate profile with the logged-in user
            
            # Save user details (first name, last name, and email)
            request.user.first_name = request.POST.get('first_name', request.user.first_name)
            request.user.last_name = request.POST.get('last_name', request.user.last_name)
            request.user.email = request.POST.get('email', request.user.email)
            request.user.save()
            
            profile.save()
            return redirect('profile')  # Redirect to profile page after saving
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'registration/add_profile.html', {
        'form': form,
        'user': request.user
    })

@login_required(login_url='login')
def delete_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        profile.delete()
        return redirect('profile')
    return render(request, 'registration/confirm_delete.html', {'profile': profile})

@login_required(login_url='login')
def order_details(request, order_id):
    """
    View to display details of a specific order.
    """
    # Fetch the order by ID and ensure it belongs to the logged-in user
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Fetch the related order items
    order_items = order.order_item_set.all()
    return render(request, 'cart/order_detail.html', {'order': order, 'order_items': order_items})

@login_required(login_url='login')
def cancel_order(request, order_id):
    print(order_id)
    if request.method == "POST":
        # Fetch the order
        order = get_object_or_404(Order, id=order_id, user=request.user)
        payment_id= order.payment_id
        # Fetch order items
        order_items = Order_item.objects.filter(order=order)
        
        # Fetch or initialize the wallet
        wallet = get_object_or_404(Wallet, user=request.user)
        
        # Check if the order is already cancelled
        if order.status == "Cancelled":
            messages.info(request, "This order is already cancelled.")
            #return redirect('order_details', order_id=order.id)
        
        # Cancel the order
        order.status = "Cancelled"
        order.save()
        messages.info(request, "This order is cancelled.")

        for item in order_items:
                product = get_object_or_404(Product, name=item.product)  # Assuming `Order_item.product` stores the product name
                product.stock += int(item.quantity)  # Add the quantity back to stock
                product.save()
            
        # If the payment mode was Razorpay, refund to wallet
        if order.payment_mode == "razorpay" or order.payment_mode == "buy-now":
                        # Get the paid_amt from the Order_data_store model
            order_data = Order_data_store.objects.filter(order_id=payment_id).first()
            
            if order_data:
                refund_amount = order_data.paid_amt
                print(refund_amount)
                # Update wallet balance
                wallet.balance += refund_amount
                wallet.save()

                # Set the paid_amt to 0 after refund
                order_data.paid_amt = 0
                order_data.save()
            messages.success(
                request, 
                f"Your order has been successfully cancelled. ₹{refund_amount} has been credited to your wallet."
            )
            if order_data.coupon_used==True:
                order_data.coupon_used =False
                order_data.save()
                user_coupon=UserCoupon.objects.filter(user=request.user)   
                user_coupon.delete()
            messages.success(request, "Your order has been successfully cancelled.")
        
        return redirect('order_details', order_id=order.id)
    
@login_required(login_url='login')   
def return_order(request, order_id):
    if request.method == "POST":
        # Fetch the order
        order = get_object_or_404(Order, id=order_id, user=request.user)
        payment_id= order.payment_id
        # Fetch order items
        order_items = Order_item.objects.filter(order=order)
        
        # Fetch or initialize the wallet
        wallet = get_object_or_404(Wallet, user=request.user)
        
        # Check if the order is already cancelled
        if order.status == "Returned":
            messages.info(request, "This order is already cancelled.")
            return redirect('order_details', order_id=order.id)
        
        # Return the order
        order.status = "Return Requested"
        order.save()
        messages.info(request, "This order is Returned.")
        if order.payment_mode == "razorpay":
                        # Get the paid_amt from the Order_data_store model
            order_data = Order_data_store.objects.filter(order_id=payment_id).first()

            if order_data:
                refund_amount = order_data.paid_amt
                print(refund_amount)
                # Update wallet balance
                wallet.balance += refund_amount
                wallet.save()
                
                messages.success(
            request, 
            f"Your order has been successfully cancelled. ₹{refund_amount} has been credited to your wallet."
        )
            # Set the paid_amt to 0 after refund
            
        for item in order_items:
            product = get_object_or_404(Product, name=item.product)  # Assuming `Order_item.product` stores the product name
            product.stock += int(item.quantity)  # Add the quantity back to stock
            product.save()
        
        
            
        
        
        return redirect('order_details', order_id=order.id)
@login_required(login_url='login')        
def profile_change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        # Basic validation
        if not pass1 or not pass2 or not old_password:
            messages.error(request, "All fields are required.")
            return render(request, 'registration/profile.html')

        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'registration/profile.html')

        try:
            user = request.user
            # Check if the old password is correct
            if not user.check_password(old_password):
                messages.error(request, "Incorrect old password.")
                return render(request, 'registration/profile.html')
            
            # Update the user's password
            user.set_password(pass1)
            user.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in after password change
            messages.success(request, "Password updated successfully!")
            return redirect('login')  # Redirect to login page after successful password change

        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return render(request, 'registration/profile.html')

    else:
        return render(request, 'registration/profile.html')

def generate_pdf_report(request, order_id):
    # Fetch the order details from the database
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Fetch the related order items
    order_items = order.order_item_set.all()

    # Load the HTML template
    template = get_template('registration/order_pdf_template.html')
    context = {
    'order': order,
    'order_items': order_items,
    }
    html = template.render(context)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order_id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error while generating PDF', status=500)

    return response
@login_required(login_url='login') 
def payment_failed_order_details(request,order_id):
        # Fetch the order by ID and ensure it belongs to the logged-in user
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Fetch the related order items
    order_items = order.order_item_set.all()
    product=Product.objects.all()
    return render(request, 'cart/payment_failed_place_order.html', {'order': order, 'order_items': order_items, 'product':product})

@login_required(login_url='login') 
def contact_us_list(request):
    contacts = Contact_us.objects.all().order_by('-date')  # Latest messages first
    return render(request, 'admin_temp/contact_us_list.html', {'contacts': contacts})
@login_required(login_url='login') 
def contact_us_detail(request, contact_id):
    contact = get_object_or_404(Contact_us, id=contact_id)
    return JsonResponse({
        'name': contact.name,
        'email': contact.email,
        'subject': contact.subject,
        'message': contact.message,
        'date': contact.date.strftime('%Y-%m-%d %H:%M'),
    })