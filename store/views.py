from django.shortcuts import render, redirect
from store . models import *
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
import random
from django.http import JsonResponse
from django.core.cache import cache
from django.contrib.auth.decorators import login_required

from django.contrib.auth.password_validation import validate_password

# Create your views here.

def PRODUCT(request):
    product=Product.objects.filter(status='Publish')
    categories=Categories.objects.all()
    filter_price=Filter_Price.objects.all()
    color=Color.objects.all()
    brand=Brand.objects.all()
    
    
    CATID=request.GET.get('categories')
    
    PRICE_FILTER_ID= request.GET.get('filter_price')
    
    COLORID = request.GET.get('color')
    
    BRANDID = request.GET.get('brand')
    
    ATOZID = request.GET.get('ATOZ')
    
    ZTOAID=request.GET.get('ZTOA')
    
    PRICE_LOWTOHIGHID=request.GET.get('PRICE_LOWTOHIGH')
    
    PRICE_HIGHTOLOWID=request.GET.get('PRICE_HIGHTOLOW')
    
    NEW_PRODUCTID = request.GET.get('NEW_PRODUCT')
    
    OLD_PRODUCTID = request.GET.get('OLD_PRODUCT')
    
    if CATID:
        product=Product.objects.filter(categories = CATID,status='Publish')
    elif PRICE_FILTER_ID:
        product=Product.objects.filter(filter_price = PRICE_FILTER_ID)
    
    elif COLORID:
        product = Product.objects.filter(color=COLORID,status='Publish')
        
    elif BRANDID:
        product=Product.objects.filter(brand=BRANDID,status='Publish')
        
    elif ATOZID:
        product=Product.objects.filter(status='Publish').order_by('name')
        
    elif ZTOAID:
        product=Product.objects.filter(status='Publish').order_by('-name')
        
    elif PRICE_LOWTOHIGHID:
        product=Product.objects.filter(status='Publish').order_by('price')
        
    elif PRICE_HIGHTOLOWID:
        product=Product.objects.filter(status='Publish').order_by('-price')
        
    elif NEW_PRODUCTID:
        product=Product.objects.filter(status='Publish',condition='New').order_by('-id')
        
    elif OLD_PRODUCTID:
        product=Product.objects.filter(status='Publish',condition='Old').order_by('id')
        
    else:
        product=Product.objects.filter(status ='Publish').order_by('id')
        
    
        
        
    context={
        'product': product,
        'categories':categories,
        'filter_price':filter_price,
        'color': color,
        'brand' : brand
    }
    
    return render(request,'main/product.html',context)

def SEARCH(request):
    query=request.GET.get('query')
    product = Product.objects.filter(name__icontains=query)
    
    context={
        'product': product
    }
    return render(request,"main/search.html",context)

def PRODUCT_DETAIL_PAGE(request,id):
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
    return render(request,'main/single_product.html',context)


def CONTACT_PAGE(request):
    if request.method == 'POST':
        name=request.POST.get('name')
        email= request.POST.get('email')
        subject= request.POST.get('subject')
        message=request.POST.get('message')
        
        contact= Contact_us(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )
        subject=subject
        message=message
        email_from=settings.EMAIL_HOST_USER
        try:
            send_mail(subject,message,email_from,['cincygreejith@gmail.com'])
            contact.save()
            return redirect('home')
        except:
            return redirect('contact')
    return render(request,'main/contact.html')