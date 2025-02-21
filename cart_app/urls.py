from .  import views
from django.urls import path

urlpatterns = [
    path('cart/add/<int:id>', views.cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>', views.item_clear, name='item_clear'),
    path('cart/item_increment/<int:id>',views.item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>',views.item_decrement, name='item_decrement'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    #path('cart/qty_update<int:id>',views.quantity_update, name='qty_update'),
    path('cart/decrement/<int:id>',views.item_decrement, name='item_decrement'),
    #path('cart/cart_clear', views.cart_clear, name='cart_clear'),
    path('cart/cart_detail',views.cart_detail,name='cart_detail'),
    path('cart/update_quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    
    path('wishlist/add/<int:product_id>', views.add_to_wishlist, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>', views.remove_from_wishlist, name='wishlist_remove'),
    path('wishlist', views.wishlist_view, name='wishlist_view'),
    
    path('add_user_coupon', views.add_user_coupon, name='add_user_coupon'),
    
    path('cart/checkout', views.address_list, name='address_list'),
    path('cart/checkout/add', views.add_address, name='add_address'),
    path('addresses/edit/<int:pk>', views.edit_address, name='edit_address'),
    path('addresses/delete/<int:pk>', views.delete_address, name='delete_address'),
    
    path('cart/checkout/placeorder', views.place_order, name='place_order'),
    path('cart/checkout/cod_placeorder', views.cod_place_order, name='cod_place_order'),
    #path('cart/checkout/cod_placeorder/db', views.cod_place_order_db, name='cod_place_order_db'),
    path('cart/checkout/razor_placeorder', views.razor_place_order, name='razor_place_order'),
    path('cart/checkout/clear', views.clear_session, name='clear_session'),
    path('handle-payment', views.handle_payment, name='handle_payment'),
    path('thanku',views.thanku, name='thanku'),
    
    path('payment-failure', views.payment_failure, name='payment_failure'),
]
