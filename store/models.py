from django.db import models

from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Avg

# Create your models here.
class Categories(models.Model):
    name=models.CharField(max_length=200)
    category_coupen=models.IntegerField
    
    def __str__(self):
        return self.name

    def get_category_active_offer(self):
        category_active_offer = self.categoryoffer_set.filter(is_active=True).first()
        print(category_active_offer)
        return category_active_offer
    
    
class Brand(models.Model):
    name=models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Color(models.Model):
    name= models.CharField(max_length=200)
    code=models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Filter_Price(models.Model):
    FILTER_PRICE=(
        ('1000 to 5000','1000 to 5000'),
        ('5000 to 10000','5000 to 10000'),
        ('10000 to 20000','10000 to 20000'),
        ('20000 to 35000','20000 to 35000'),
        ('35000 to 50000','35000 to 50000'),
        ('50000 to 100000','50000 to 100000'),
        ('100000 & Above', '1000000 & Above')
    )
    price=models.CharField(choices=FILTER_PRICE,max_length=60)
    
    def __str__(self):
        return self.price
    


class Product(models.Model):
    CONDITION = (('New','New'),('Old','Old'),('OUT OF STOCK','OUT OF STOCK'))
    STOCK = (('IN STOCK','IN STOCK'),('OUT OF STOCK','OUT OF STOCK'))
    STATUS=('Publish','Publish'),('Draft','Draft')
    
    unique_id=models.CharField(unique=True,max_length=200,null=True,blank=True)
    image=models.ImageField(upload_to='Product_images/img')
    name=models.CharField(max_length=200)
    price=models.IntegerField()
    condition= models.CharField(choices=CONDITION,max_length=100)
    information= models.TextField()
    description= models.TextField()
    
    stock=models.CharField(choices=STOCK,max_length=200)
    status = models.CharField(choices=STATUS,max_length=200)
    created_date=models.DateTimeField(default=timezone.now)
    categories= models.ForeignKey(Categories, on_delete=models.CASCADE)
    brand=models.ForeignKey(Brand, on_delete=models.CASCADE)
    color=models.ForeignKey(Color,on_delete=models.CASCADE)
    filter_price=models.ForeignKey(Filter_Price,on_delete=models.CASCADE)
    stock=  models.BigIntegerField()
    
    
    def save(self, *args, **kwargs):
        if self.unique_id is None and self.created_date and self.id:
            self.unique_id=self.created_date.strftime('75%Y%m%d23') + str(self.id)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def avg_rating(self):
        #reviews=self.Review.all()
        reviews=Review.objects.all()
        if reviews:
            return Review.objects.filter(product=self).aggregate(Avg('rating'))['rating__avg']
        return 0

    def total_reviews(self):
        return Review.objects.filter(product=self).count()
    
    def get_active_offer(self):
        """
        Returns the active offer for the product if it exists, otherwise None.
        """
        active_offer = self.productoffer_set.filter(is_active=True).first()
        print (active_offer)
        return active_offer
    
    
class Images(models.Model):
    image=models.ImageField(upload_to='Product_images/img')
    product= models.ForeignKey(Product,on_delete=models.CASCADE)
    

class Tag(models.Model):
    name= models.CharField(max_length=200)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name


class Contact_us(models.Model):
    name=models.CharField(max_length=200)
    email=models.EmailField(max_length=200)
    subject=models.CharField(max_length=300)
    message=models.TextField()
    date = models.DateTimeField( auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Review(models.Model):
    user= models.ForeignKey(User,related_name='review',on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    comment=models.TextField(max_length=1000)
    rating=models.IntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    status= models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.id)
    
    def avg_rating(self):
        reviews=self.review.all()
        if reviews.exist():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0

    def total_reviews(self):
        return self.comment.count()