from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime, timedelta

# Create your models here.

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=datetime.now() + timedelta(minutes=10))

    def is_valid(self):
        return datetime.now() < self.expires_at
    
class  Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='Profile')
    country = models.CharField(max_length=100)
    address = models.CharField(max_length=600)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10)
    phone = models.CharField(max_length=20)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


    
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.IntegerField()  # Monetary balance

    def __str__(self):
        return f"{self.user.username}'s Wallet - Balance: {self.balance}"

    
    def __str__(self):
        return self.user.username

