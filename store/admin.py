from django.contrib import admin
from . models import *

# Register your models here.
class ImageTabularinline(admin.TabularInline):
    model=Images


class TagTabularinline(admin.TabularInline):
    model=Tag

class ProductAdmin(admin.ModelAdmin):
    inlines=[ImageTabularinline,TagTabularinline]
    
admin.site.register(Categories)
admin.site.register(Brand)
admin.site.register(Color)
admin.site.register(Filter_Price)
admin.site.register(Product,ProductAdmin)
admin.site.register(Images)
admin.site.register(Tag)
admin.site.register(Contact_us)
admin.site.register(Review)
