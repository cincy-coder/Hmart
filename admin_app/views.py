# views.py
from django.shortcuts import render, redirect,get_object_or_404
from store.models import *
from django.contrib.auth.models import User
from .forms import *
from django.http import Http404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms import modelformset_factory
from .forms import ProductForm, ImagesInlineFormSet, TagInlineFormSet
from cart_app.models import *
from django.db.models import Sum, Count

from django.utils.timezone import now, timedelta
from datetime import datetime, timedelta
from django.views.generic import CreateView, DeleteView
from cart_app.models import *
from django.urls import reverse_lazy

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

@login_required(login_url='login')
def create_product(request, product_id=None):
    product = get_object_or_404(Product, id=product_id) if product_id else Product()

    product_form = None
    images_formset = None
    tags_formset = None

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        images_formset = ImagesInlineFormSet(request.POST, request.FILES, instance=product)
        tags_formset = TagInlineFormSet(request.POST, instance=product)

        if product_form.is_valid() and images_formset.is_valid() and tags_formset.is_valid():
            product = product_form.save()
            images_formset.save()
            tags_formset.save()
            return redirect('product_list')
    else:
        product_form = ProductForm(instance=product)
        images_formset = ImagesInlineFormSet(instance=product)
        tags_formset = TagInlineFormSet(instance=product)

    return render(
        request,
        'admin_temp/add_product.html',
        {'product_form': product_form, 'images_formset': images_formset, 'tags_formset': tags_formset}
    )
    
    
@login_required(login_url='login')    
def add_new_product(request, product_id=None):
    product = get_object_or_404(Product, id=product_id) if product_id else Product()

    product_form = None
    images_formset = None
    tags_formset = None

    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        images_formset = ImagesInlineFormSet(request.POST, request.FILES, instance=product)
        tags_formset = TagInlineFormSet(request.POST, instance=product)

        if product_form.is_valid() and images_formset.is_valid() and tags_formset.is_valid():
            product = product_form.save()
            images_formset.save()
            tags_formset.save()
            return redirect('product_list')
    else:
        product_form = ProductForm(instance=product)
        images_formset = ImagesInlineFormSet(instance=product)
        tags_formset = TagInlineFormSet(instance=product)

    return render(
        request,
        'admin_temp/add_product.html',
        {'product_form': product_form, 'images_formset': images_formset, 'tags_formset': tags_formset}
    )
    
@login_required(login_url='login')    
def  product_list(request):
    product=Product.objects.filter(status='Publish')
    categories=Categories.objects.all()
    filter_price=Filter_Price.objects.all()
    brand=Brand.objects.all()
    
    CATID=request.GET.get('categories')
    
    PRICE_FILTER_ID= request.GET.get('filter_price')
    
    BRANDID = request.GET.get('brand')
    
    NEW_PRODUCTID = request.GET.get('NEW_PRODUCT')
    
    OLD_PRODUCTID = request.GET.get('OLD_PRODUCT')
    
    STATUS_PUBLISHED= request.GET.get('status_published')
    
    STATUS_DRAFT= request.GET.get('status_drafted')
    
    if CATID:
        product=Product.objects.filter(categories = CATID)
        
    elif PRICE_FILTER_ID:
        product=Product.objects.filter(filter_price = PRICE_FILTER_ID)
    
        
    elif BRANDID:
        product=Product.objects.filter(brand=BRANDID)
        
    elif STATUS_PUBLISHED:
        product=Product.objects.filter(status='Publish') 
        
    elif STATUS_DRAFT:
        product=Product.objects.filter(status='Draft')     
        
    elif NEW_PRODUCTID:
        product=Product.objects.filter(condition='New').order_by('-id')
        
    elif OLD_PRODUCTID:
        product=Product.objects.filter(condition='Old').order_by('id')
        
    else:
        product=Product.objects.all().order_by('id')

    context={
        'product': product,
        'categories':categories,
        'filter_price':filter_price,
        'brand' : brand
    }
    return render(request,'admin_temp/product_list.html',context)

@login_required(login_url='login')
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.status = "Draft"
    product.save()
    return redirect('product_list')

def restore_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.status = "Publish"
    product.save()
    return redirect('restore_product_again')

def restore_product_again(request):
    product=Product.objects.filter(status='Draft')
    context= {'product':product}
    return render(request,'admin_temp/admin_product_restore.html',context)

def permanent_delete(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('restore_product_again')

@login_required(login_url='login')
def admin_single_product_list(request,id):
    prod=Product.objects.filter(id=id).first()
    context={
        'prod': prod,
    }
    
    # Product Review
    if request.method =="POST":
        star_rating = request.POST.get('rating')
        product_review= request.POST.get('review_text')
        user=request.user
        product_review_save=Review(user=user,product=prod,comment=product_review,rating=star_rating)
        product_review_save.save()
    return render(request,'admin_temp/admin_single_product.html',context)

@login_required(login_url='login')
def user_list(request):
    user=User.objects.all()
    user_blocked = request.GET.get('user_blocked')
    user_active = request.GET.get('user_active')
    user_staff= request.GET.get('user_staff')
    user_customer= request.GET.get('user_customer')
    
    if user_blocked:
        user=User.objects.filter(is_active=False).order_by('-id') 
        
    elif user_active:
        user=User.objects.filter(is_active=True).order_by('-id')     
        
    elif user_customer:
        user=User.objects.filter(is_staff=False).order_by('-id')
        
    elif user_staff:
        user=User.objects.filter(is_staff=True).order_by('-id')
        
    else:
        user=User.objects.all().order_by('id')

    context={
        'user': user,
    }
    return render(request,'admin_temp/user_list.html',context)

@login_required(login_url='login')
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm(instance=user)
    
    return render(request, 'admin_temp/edit_user.html', {'form': form})

@login_required(login_url='login')
# View to add, edit and delete categories, brands, and colors
def manage_variants(request):
    # Handling POST requests for adding new entries
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'category':
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manage_variants')

        elif form_type == 'brand':
            form = BrandForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manage_variants')

        elif form_type == 'color':
            form = ColorForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manage_variants')

    # Fetch existing data for display
    categories = Categories.objects.all()
    brands = Brand.objects.all()
    colors = Color.objects.all()

    return render(request, 'admin_temp/varients.html', {
        'category_form': CategoryForm(),
        'brand_form': BrandForm(),
        'color_form': ColorForm(),
        'categories': categories,
        'brands': brands,
        'colors': colors,
    })

def edit_category(request, pk):
    category = get_object_or_404(Categories, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('manage_variants')  # Redirect back to the list
    else:
        form = CategoryForm(instance=category)

    return render(request, 'admin_temp/edit_category.html', {'form': form, 'category': category})


# Similar views for brands and colors:
def edit_brand(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand updated successfully!")
            return redirect('manage_variants')
    else:
        form = BrandForm(instance=brand)

    return render(request, 'admin_temp/edit_brand.html', {'form': form, 'brand': brand})


def edit_color(request, pk):
    color = get_object_or_404(Color, pk=pk)
    if request.method == 'POST':
        form = ColorForm(request.POST, instance=color)
        if form.is_valid():
            form.save()
            messages.success(request, "Color updated successfully!")
            return redirect('manage_variants')
    else:
        form = ColorForm(instance=color)

    return render(request, 'admin_temp/edit_color.html', {'form': form, 'color': color})


def delete_category(request, category_id):
    category = get_object_or_404(Categories, id=category_id)
    category.delete()
    return redirect('manage_variants')

def delete_brand(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    brand.delete()
    return redirect('manage_variants')

def delete_color(request, color_id):
    color = get_object_or_404(Color, id=color_id)
    color.delete()
    return redirect('manage_variants')


def edit_order(request, order_id):
    # Fetch the order based on the given order_id
    order = get_object_or_404(Order, id=order_id)
    
    # Handle the edit form (this is just an example)
    if request.method == 'POST':
        # Process the form data
        order.status = request.POST.get('status')
        order.save()
        return redirect('admin_home')  # Redirect back to the order list
    
    # If GET request, display the order edit form
    return render(request, 'admin_temp/edit_order.html', {'order': order})

def get_sales_report(request):
        # Default filter: All orders
    orders = Order.objects.all()  # Consider only paid orders

    # Get filter type from query parameters
    filter_type = request.GET.get('filter', 'custom')  # daily, weekly, monthly, yearly, custom
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    count=orders.count() # Number of
    discounted_orders_count = Order_data_store.objects.filter(discount_percentage__gt=0).count()

    print(f"Number of orders with discounts applied: {discounted_orders_count}")

    # Filter based on type
    if filter_type == 'daily':
        orders = orders.filter(date=now().date())
    elif filter_type == 'weekly':
        week_start = now() - timedelta(days=now().weekday())
        orders = orders.filter(date__gte=week_start, date__lte=now().date())
    elif filter_type == 'monthly':
        orders = orders.filter(date__year=now().year, date__month=now().month)
    elif filter_type == 'yearly':
        orders = orders.filter(date__year=now().year)
    elif filter_type == 'custom' and start_date and end_date:
        orders = orders.filter(date__gte=start_date, date__lte=end_date)

    # Aggregate Data
    total_sales_count = orders.count()
    total_order_amount = orders.aggregate(Sum('amount'))['amount__sum'] or 0.0

    # Fetch order items for detailed analysis
    order_items = Order_item.objects.filter(order__in=orders)
    total_quantity = order_items.aggregate(Sum('quantity'))['quantity__sum'] or 0

    context = {
        'orders': orders,
        'order_items': order_items,
        'total_sales_count': total_sales_count,
        'total_order_amount': int(total_order_amount),
        'total_quantity': total_quantity,
        'discount_orders_count': discounted_orders_count,
    }

    return render(request, 'admin_temp/report.html', context)






class CouponCreateView(CreateView):
    model = Coupon
    fields = ['code', 'discount_amount', 'expiry_date', 'is_active']
    template_name = 'admin_temp/coupon_create.html'
    success_url = reverse_lazy('coupon_list')
# Delete an existing coupon
class CouponDeleteView(DeleteView):
    model = Coupon
    template_name = 'admin_temp/coupon_confirm_delete.html'
    success_url = reverse_lazy('coupon_list')

def coupon_list(request):
    coupons = Coupon.objects.only('code', 'discount_amount', 'expiry_date', 'is_active')
    return render(request, 'admin_temp/coupon_list.html', {'coupons': coupons})

def create_product_offer(request):
    if request.method == 'POST':
        form = ProductOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_offer_list')  # Redirect to offer list or another page
    else:
        form = ProductOfferForm()
    return render(request, 'admin_temp/create_product_offer.html', {'form': form})

def create_category_offer(request):
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_offer_list')
    else:
        form = CategoryOfferForm()
    return render(request, 'admin_temp/create_category_offer.html', {'form': form})

def product_offer_list(request):
    product_offers = ProductOffer.objects.all()  # Get all product offers
    return render(request, 'admin_temp/product_offer_list.html', {'product_offers': product_offers})


def delete_product_offer(request, offer_id):
    offer = get_object_or_404(ProductOffer, id=offer_id)
    offer.delete()
    return redirect('product_offer_list')  # Redirect back to the offer list

def category_offer_list(request):
    category_offers = CategoryOffer.objects.all()  # Get all category offers
    return render(request, 'admin_temp/category_offer_list.html', {'category_offers': category_offers})


def delete_category_offer(request, offer_id):
    offer = get_object_or_404(CategoryOffer, id=offer_id)
    offer.delete()
    return redirect('category_offer_list')  # Redirect back to the offer list

def generate_sales_pdf(request):
    # Fetch filtered data
    orders = Order.objects.all()
    count=orders.count()
    filter_type = request.GET.get('filter', 'custom')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if filter_type == 'daily':
        orders = orders.filter(date=now().date())
    elif filter_type == 'weekly':
        week_start = now() - timedelta(days=now().weekday())
        orders = orders.filter(date__gte=week_start, date__lte=now().date())
    elif filter_type == 'monthly':
        orders = orders.filter(date__year=now().year, date__month=now().month)
    elif filter_type == 'yearly':
        orders = orders.filter(date__year=now().year)
    elif filter_type == 'custom' and start_date and end_date:
        orders = orders.filter(date__gte=start_date, date__lte=end_date)

    # Aggregate Data
    total_sales_count = orders.count()
    total_order_amount = orders.aggregate(Sum('amount'))['amount__sum'] or 0.0
    order_items = Order_item.objects.filter(order__in=orders)
    total_quantity = order_items.aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Render template to string
    context = {
        'orders': orders,
        'order_items': order_items,
        'total_sales_count': total_sales_count,
        'total_order_amount': total_order_amount,
        'total_quantity': total_quantity,
    }
    html = render_to_string('admin_temp/sales_report_pdf.html', context)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('An error occurred while generating the PDF.', status=500)
    return response


def inventory(request):
    return render(request, 'admin_temp/inventory.html')

def admin_order(request):
    return render(request, 'admin_temp/admin_orders.html')
