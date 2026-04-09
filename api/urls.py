from django.urls import path,include
from rest_framework_nested import routers

from product.views import ProductViewSet, CategoryViewSet ,ReviewViewSet, ProductImageViewSet,SellerProductViewSet
from order.views import CartViewSet,CartItemViewSet,OrderViewSet, SellerOrderViewSet, WishlistViewSet
from users.views import DepositView , UserRoleManagementViewSet
from order.views import SSLCommerzPaymentView, SSLCommerzIPNView
from users.views import UserProfileView

router = routers.DefaultRouter()

router.register('products', ProductViewSet ,basename='products')
router.register('categories', CategoryViewSet)
router.register('carts',CartViewSet, basename='carts')
router.register('orders',OrderViewSet, basename='orders')
router.register('wishlist', WishlistViewSet, basename='wishlist')
router.register('admin/users', UserRoleManagementViewSet, basename='admin-users')
router.register('seller-products', SellerProductViewSet, basename='seller-products')
router.register('seller-orders', SellerOrderViewSet, basename='seller-orders')


product_router = routers.NestedDefaultRouter(router,'products',lookup='product')
product_router.register('reviews',ReviewViewSet,basename='product-review')
product_router.register('images',ProductImageViewSet,basename='product-images')

cart_router = routers.NestedDefaultRouter(router,'carts',lookup='cart')
cart_router.register('items',CartItemViewSet,basename='cart_item')


urlpatterns = [
    path('',include(router.urls)),
    path('',include(product_router.urls)),
    path('',include(cart_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('deposit/', DepositView.as_view(), name='deposit'),
    # path("create-checkout-session/", CreateStripeSessionView.as_view(), name="create-checkout-session"),
    path("create-sslcommerz-session/", SSLCommerzPaymentView.as_view(), name="sslcommerz-session"),
    path("sslcommerz-ipn/", SSLCommerzIPNView.as_view(), name="sslcommerz-ipn"),
    path('users/profile/', UserProfileView.as_view(), name='user-profile'),

]