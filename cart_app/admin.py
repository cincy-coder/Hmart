from django.contrib import admin
from . models import *
from cart_app.models import Coupon

# Register your models here.
class OrderItemTubularInline(admin.TabularInline):
    model = Order_item

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemTubularInline]

admin.site.register(Order,OrderAdmin)
admin.site.register(Order_item)
admin.site.register(Address)
admin.site.register(Wishlist)

admin.site.register(Coupon)
admin.site.register(UserCoupon)
@admin.register(ProductOffer)
class ProductOfferAdmin(admin.ModelAdmin):
    list_display = ['product', 'discount_percentage', 'start_date', 'end_date', 'is_active']


@admin.register(CategoryOffer)
class CategoryOfferAdmin(admin.ModelAdmin):
    list_display = ['category', 'discount_percentage', 'start_date', 'end_date', 'is_active']
admin.site.register(Order_data_store)