from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView # useful in displaying index.html template


urlpatterns = [
    path('product',views.PRODUCT,name='product'),
    path('search',views.SEARCH,name='search'),
    path('contact',views.CONTACT_PAGE,name='contact'),
    path('product/<str:id>',views.PRODUCT_DETAIL_PAGE,name='product_detail'),
    path('reviews',views.Review,name='reviews'),
]

