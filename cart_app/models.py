from django.db import models
from django.contrib.auth.models import User
from  store.models import *

# Create your models here.
class Address(models.Model):
    user= models.ForeignKey(User, on_delete=models.CASCADE)
    firstname=models.CharField(max_length=100)
    lastname=models.CharField(max_length=100)
    country=models.CharField(max_length=100)
    address=models.CharField(max_length=200)
    city=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    postcode=models.IntegerField()
    phone=models.IntegerField()
    email= models.EmailField(max_length=100)
    
    
    def __str__(self):
        return f"{self.firstname}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

    class Meta:
        unique_together = ('user', 'product')


STATUS_CHOICES = (
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancel', 'Cancel'),
    ('Return Requested', 'Return Requested'),
    ("Return Accepted", 'Return Accepted'),
    ('Payment Failed', 'Payment Failed'),
)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    amount = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=300,null=True,blank=True)
    payment_mode = models.CharField(max_length=100)
    paid = models.BooleanField(default=False,null=True)
    status=models.CharField(max_length=54,choices=STATUS_CHOICES,default='Pending')
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username
    
class Order_item(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    product= models.CharField(max_length=200)
    image=models.ImageField(upload_to='Product_Images/Order_Img')
    quantity=models.CharField(max_length=20)
    price = models.CharField(max_length=50)
    total = models.CharField(max_length=1000)
    
    def __str__(self):
        return self.order.user.username
    
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_amount = models.IntegerField()
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        #Checks if the coupon is active and not expired.
        return self.is_active and self.expiry_date >= timezone.now().date()
        
class UserCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_coupons")
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usercoupons")
    redeemed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.coupon.code}"


class ProductOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_percentage = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Offer on {self.product.name}"
    
class CategoryOffer(models.Model):
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    discount_percentage = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Offer on {self.category.name} category"


class Order_data_store(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=200,null=True,blank=True)
    total_amt = models.IntegerField()
    paid_amt = models.IntegerField()
    discount_percentage = models.IntegerField()
    coupon_used = models.BooleanField()
    
    def calculate_discounted_total(self):
        """
        Calculate the discounted total amount if a discount is applied.
        If discount_percentage is 0, return the total_amt.
        """
        if self.discount_percentage > 0:
            discount = (self.total_amt * self.discount_percentage) / 100
            return self.total_amt - discount
        return self.total_amt
    