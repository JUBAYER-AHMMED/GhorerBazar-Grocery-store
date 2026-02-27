from django.shortcuts import render
from django.db.models import Prefetch

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework import status
from order.models import Cart,CartItem,Order,OrderItem, Wishlist
from order.serializers import CartSerializer,CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer, EmptySerializer, WishlistSerializer, SellerOrderSerializer
from order.services import OrderService

# Create your views here.
class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    """
    API endpoint for managing cart in the grocery store
     - Allows authenticated user to create , update, delete cart
     
    """
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return Cart.objects.prefetch_related('items__product').filter(user = self.request.user)
    serializer_class = CartSerializer
    permission_classes=[IsAuthenticated]

    # def perform_create(self, serializer):
    #     print("cartviewset perform create called")
    #     serializer.save(user=self.request.user)
    def create(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)

        serializer = self.get_serializer(cart)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )



class CartItemViewSet(ModelViewSet):
    """
    API endpoint for managing cart items
     - Allows authenticated user to view their cart items in their cart
     - Allows authenticated user to create , update, delete cartitems from their cart
    """
    # queryset = CartItem.objects.all()
    # serializer_class = CartItemSerializer 
    http_method_names=['get','post','patch','delete']
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if getattr(self,'swagger_fake_view', False):
            return context
        return {'cart_id': self.kwargs['cart_pk']}

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        # return CartItem.objects.select_related('product').filter(cart_id = self.kwargs['cart_pk'])
        return CartItem.objects.select_related('product').filter(cart_id = self.kwargs.get('cart_pk'))
    
    def create(self, request, *args, **kwargs):
        # print("cart_pk:", kwargs.get('cart_pk'))
        # print("request.data:", request.data)
        # print("request.user:", request.user)
        return super().create(request, *args, **kwargs)
        
class OrderViewSet(ModelViewSet):
    """
    API endpoint for managing orders
     - Allows authenticated user to create , update, cancel orders
     - Allows authenticated user to view their purchase history
    """
    http_method_names = ['get','post','patch','delete','head','options']
    
    @action(detail=True, methods=['post'])
    def cancel(self,request, pk=None):
        order = self.get_object()
        OrderService.cancel_order(order=order, user=request.user)
        return Response({'status':'order cancled'})
    
    @action(detail=True,methods=['patch'])
    def update_status(self,request,pk=None):
        order = self.get_object()
        serializer = UpdateOrderSerializer(order,data = request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': f"status updated successfully to {request.data['status']}"})
    
    @action(detail=False, methods=['get'], url_path='my-purchase-history')
    def purchase_history(self, request):
        orders = Order.objects.prefetch_related('items__product').filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def get_permissions(self):
        if self.action in ['update_status','destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if self.request.user.is_staff:
            return Order.objects.prefetch_related('items__product').all()
        return Order.objects.prefetch_related('items__product').filter(user= self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'cancel':
            return EmptySerializer
        # if self.request.method == 'POST':
        #     return CreateOrderSerializer
        if self.action == 'create':
            return CreateOrderSerializer
        # elif self.request.method == 'PATCH':
        #     return UpdateOrderSerializer
        elif self.action == 'update_status':
            return UpdateOrderSerializer
        return OrderSerializer
    
    def get_serializer_context(self):
        if getattr(self, 'swagger_fake_view', False):
            return super().get_serializer_context()
        return {'user_id': self.request.user.id, 'user':self.request.user}
    



class WishlistViewSet(ModelViewSet):
    '''
    To add in wishlish
    method: POST 
    endpoint: /api/v1/wishlist/
    value for example:
    {
        "product_id": 5
    }
    '''
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

    def get_serializer_context(self):
        return {'request': self.request}
    


class SellerOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Dashboard for sellers:
    - List orders that include products created by the logged-in seller
    - Read-only: cannot edit orders
    """
    serializer_class = SellerOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 'seller' and not user.is_staff:
            return Order.objects.none()  

        seller_items = OrderItem.objects.filter(product__seller=user)
        return Order.objects.prefetch_related(
            Prefetch('items', queryset=seller_items, to_attr='seller_items')
        ).filter(items__product__seller=user).distinct()
    

# order/views.py
# order/views.py
import json
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import SSLCommerzPaymentSerializer
from order.models import Cart

class SSLCommerzPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SSLCommerzPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_id = serializer.validated_data['cart_id']

        cart = Cart.objects.prefetch_related('items__product').get(pk=cart_id)

        total_amount = sum([item.product.price * item.quantity for item in cart.items.all()])

        # SSLCommerz config
        store_id = settings.SSLCOMMERZ_STORE_ID
        store_pass = settings.SSLCOMMERZ_STORE_PASSWORD
        is_live = False  # False for sandbox

        payload = {
            "store_id": store_id,
            "store_passwd": store_pass,
            "total_amount": str(total_amount),
            "currency": "BDT",
            "tran_id": str(cart_id),
            "success_url": settings.SSLCOMMERZ_SUCCESS_URL,
            "fail_url": settings.SSLCOMMERZ_FAIL_URL,
            "cancel_url": settings.SSLCOMMERZ_CANCEL_URL,
            "cus_name": request.user.get_full_name(),
            "cus_email": request.user.email,
            "cus_add1": "N/A",
            "cus_city": "N/A",
            "cus_country": "Bangladesh",
            "shipping_method": "NO",
            "product_name": "Cart Order",
            "product_category": "General",
            "product_profile": "general",
        }

        api_url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php" if not is_live else "https://securepay.sslcommerz.com/gwprocess/v4/api.php"

        response = requests.post(api_url, data=payload)
        data = response.json()

        if data.get("status") == "SUCCESS":
            return Response({"payment_url": data.get("GatewayPageURL")})
        return Response({"error": "Failed to create SSLCommerz session"}, status=400)


# order/views.py
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from order.models import Cart
from order.services import OrderService
import requests

class SSLCommerzIPNView(APIView):
    """
    IPN (Instant Payment Notification) for SSLCommerz.
    Called by SSLCommerz server after payment.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        tran_id = data.get("tran_id")  # our cart_id
        val_id = data.get("val_id")    # SSLCommerz transaction ID
        status = data.get("status")    # VALID / FAILED

        if not tran_id:
            return Response({"error": "tran_id missing"}, status=400)

        try:
            cart = Cart.objects.prefetch_related('items__product').get(pk=tran_id)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=404)

        # Verify payment via SSLCommerz API
        verify_url = "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"
        if getattr(settings, "SSLCOMMERZ_LIVE", False):
            verify_url = "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php"

        params = {
            "val_id": val_id,
            "store_id": settings.SSLCOMMERZ_STORE_ID,
            "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
            "v": "1",
            "format": "json",
        }

        r = requests.get(verify_url, params=params)
        verification = r.json()

        if verification.get("status") == "VALID":
            # Payment is verified → create order
            try:
                order = OrderService.create_order(cart.user.id, cart.id)
                return Response({"success": True, "order_id": str(order.id)})
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        else:
            return Response({"success": False, "message": "Payment verification failed"}, status=400)