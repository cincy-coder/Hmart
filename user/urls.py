
from django.urls import path
from . import views


urlpatterns = [
    path('',views.HOME ,name='home'),
    path('base/',views.BASE,name='base'),
    path('register',views.HandleRegister,name='register'),
    path('login/',views.HandleLogin,name='login'),
    path('logout',views.HandleLogout,name='logout'),
    path('forget_password',views.forget_password,name='forget_password'),
    path('verify_otp',views.verify_otp,name='verify_otp'),
    path('success',views.success,name='success'),
    path('admin_home',views.ADMIN_HOME,name='admin_home'),   
    path('profile/', views.profile_view, name='profile'),
    path('profile/add_edit', views.add_edit_profile, name='add_edit_profile'),
    path('profile/delete', views.delete_profile, name='delete_profile'),
    path('profile/<int:order_id>', views.order_details, name='order_details'),
    path('profile/payment_failed<int:order_id>', views.payment_failed_order_details, name='payment_failed_order_details'),
    path('profile/<int:order_id>/cancel', views.cancel_order, name='cancel_order'),
    path('profile/<int:order_id>/return', views.return_order, name='return_order'),
    path('profile/change_password', views.profile_change_password, name='profile_change_password'),
    path('download_pdf/<int:order_id>/', views.generate_pdf_report, name='download_pdf'),
    #path('wallet',views.wallet,name='wallet'),
    path('contact-us/', views.contact_us_list, name='contact_us_list'),
    path('contact-us/<int:contact_id>/', views.contact_us_detail, name='contact_us_detail'),

]
