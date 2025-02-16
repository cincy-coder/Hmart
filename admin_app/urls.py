# urls.py
from django.urls import path
from .views import CouponCreateView, CouponDeleteView
from . import views


urlpatterns = [
    path('add_product/<int:product_id>',views.create_product,name='add_product'),
    path('admin_order', views.admin_order, name='admin_order'),
    path('product_list',views.product_list,name='product_list'),
    path('admin_single_product_list/<str:id>',views.admin_single_product_list,name='admin_single_product_list'),
    path('user_list',views.user_list,name='user_list'),
    path('edit_user/<int:user_id>', views.edit_user, name='edit_user'),
    path('add_new_product',views.add_new_product,name='add_new_product'),
    path('restore_product_again',views.restore_product_again,name='restore_product_again'),
    path('restore_products/<int:product_id>',views.restore_product, name='restore_product'),
    path('permanent_delete/<int:product_id>',views.permanent_delete, name='permanent_delete'),
    path('manage-variants', views.manage_variants, name='manage_variants'),
    path('edit_category/<int:pk>/', views.edit_category, name='edit_category'),
    path('edit_brand/<int:pk>/', views.edit_brand, name='edit_brand'),
    path('edit_color/<int:pk>/', views.edit_color, name='edit_color'),
    path('delete-category/<int:category_id>', views.delete_category, name='delete_category'),
    path('delete-brand/<int:brand_id>', views.delete_brand, name='delete_brand'),
    path('delete-color/<int:color_id>', views.delete_color, name='delete_color'),
    path('edit_order/<int:order_id>/', views.edit_order, name='edit_order'),
    
    path('sales_report',views.get_sales_report, name='sales_report'),
    
    path('coupon/create', CouponCreateView.as_view(), name='coupon_create'),
    path('coupon/delete/<int:pk>', CouponDeleteView.as_view(), name='coupon_delete'),
    path('coupons', views.coupon_list, name='coupon_list'),
    path('create-product-offer/', views.create_product_offer, name='create_product_offer'),
    path('create-category-offer/', views.create_category_offer, name='create_category_offer'),
    path('product-offers/', views.product_offer_list, name='product_offer_list'),  # List product offers
    path('delete-product-offer/<int:offer_id>/', views.delete_product_offer, name='delete_product_offer'),  # Delete product offer
    path('category-offers/', views.category_offer_list, name='category_offer_list'),  # List category offers
    path('delete-category-offer/<int:offer_id>/', views.delete_category_offer, name='delete_category_offer'),  # Delete category offer
    
    path('sales-report/pdf/', views.generate_sales_pdf, name='generate_sales_pdf'),
    
    path('inventory', views.inventory, name='inventory'),
]
