from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'firstname', 'lastname', 'country', 'address', 'city', 
            'state', 'postcode', 'phone', 'email'
        ]
