from django import forms
from store.models import *
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from cart_app.models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_active': 'Active Status',
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'unique_id', 'image', 'name', 'price', 'condition', 
            'information', 'description', 'stock', 'status', 
            'categories', 'brand', 'color', 'filter_price'
        ]
ImagesInlineFormSet = inlineformset_factory(
    Product,
    Images,
    fields=['image', 'product'],
    extra=3,  # Number of empty forms to display
    can_delete=True  # Allow deletion of related images
)

TagInlineFormSet = inlineformset_factory(
    Product,
    Tag,
    fields=['name', 'product'],
    extra=3,
    can_delete=True
)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Categories
        fields = ['name']

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name']

class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name', 'code']



class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_amount', 'expiry_date', 'is_active']
        
class ProductOfferForm(forms.ModelForm):
    class Meta:
        model = ProductOffer
        fields = ['product', 'discount_percentage', 'start_date', 'end_date', 'is_active']
        
class CategoryOfferForm(forms.ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ['category', 'discount_percentage', 'start_date', 'end_date', 'is_active']
        
