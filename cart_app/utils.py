from .models import *
from user.models import *
from datetime import date

def apply_welcome_bonus(user):
    """
    Assign a welcome bonus to the user's wallet if not already assigned.
    """
    wallet, created = Wallet.objects.get_or_create(user=user)
    if wallet.welcome_bonus > 0:
        return None  # Welcome bonus already applied

    # Fetch the first active coupon as a welcome bonus
    welcome_coupon = Coupon.objects.filter(is_active=True).first()
    if welcome_coupon:
        wallet.welcome_bonus = welcome_coupon.discount_amount
        wallet.save()
        return welcome_coupon
    return None

def use_welcome_bonus(user, order_amount):
    """
    Deduct the welcome bonus from the order amount.
    """
    wallet, _ = Wallet.objects.get_or_create(user=user)
    if wallet.welcome_bonus > 0:
        discount = min(wallet.welcome_bonus, order_amount)
        wallet.welcome_bonus -= discount
        wallet.balance = str(float(wallet.balance) - discount)
        wallet.save()
        return discount
    return 0

def reset_welcome_bonus_on_order_cancel(user):
    """
    Reset the welcome bonus to zero if an order is canceled.
    """
    wallet, _ = Wallet.objects.get_or_create(user=user)
    wallet.welcome_bonus = 0
    wallet.save()
