from django.contrib import admin
from order.models import Cart,CartItem,Order,OrderItem, Wishlist
# Register your models here.

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id','user']
# admin.site.register(Cart)
admin.site.register(CartItem)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','user','status']
# admin.site.register(Cart)
admin.site.register(OrderItem)
admin.site.register(Wishlist)